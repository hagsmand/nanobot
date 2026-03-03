#!/usr/bin/env python3
"""
Gateway wrapper that adds a simple HTTP health endpoint for Render.com free plan.
This allows the gateway to run as a Web Service (which requires an open port).
"""
import asyncio
import os
import sys
from aiohttp import web


async def health_check(request):
    """Simple health check endpoint."""
    return web.Response(text="OK", status=200)


async def start_http_server(port: int):
    """Start a minimal HTTP server for health checks."""
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"✓ HTTP health endpoint running on port {port}")
    return runner


async def run_gateway():
    """Run the nanobot gateway."""
    # Import and run the gateway command
    from nanobot.cli.commands import gateway as gateway_cmd
    from nanobot.config.loader import load_config
    
    # Start HTTP server first
    port = int(os.environ.get("PORT", "10000"))
    http_runner = await start_http_server(port)
    
    print(f"🐈 Starting nanobot gateway...")
    
    # Initialize variables that might be used in finally block
    agent = None
    heartbeat = None
    cron = None
    channels = None
    
    try:
        # Import gateway internals
        from nanobot.agent.loop import AgentLoop
        from nanobot.bus.queue import MessageBus
        from nanobot.channels.manager import ChannelManager
        from nanobot.config.loader import get_data_dir
        from nanobot.cron.service import CronService
        from nanobot.cron.types import CronJob
        from nanobot.heartbeat.service import HeartbeatService
        from nanobot.session.manager import SessionManager
        from nanobot.utils.helpers import sync_workspace_templates
        
        config = load_config()
        sync_workspace_templates(config.workspace_path)
        bus = MessageBus()
        
        # Create provider
        from nanobot.cli.commands import _make_provider
        provider = _make_provider(config)
        
        session_manager = SessionManager(config.workspace_path)
        
        # Create cron service
        cron_store_path = get_data_dir() / "cron" / "jobs.json"
        cron = CronService(cron_store_path)
        
        # Create agent
        agent = AgentLoop(
            bus=bus,
            provider=provider,
            workspace=config.workspace_path,
            model=config.agents.defaults.model,
            temperature=config.agents.defaults.temperature,
            max_tokens=config.agents.defaults.max_tokens,
            max_iterations=config.agents.defaults.max_tool_iterations,
            memory_window=config.agents.defaults.memory_window,
            reasoning_effort=config.agents.defaults.reasoning_effort,
            brave_api_key=config.tools.web.search.api_key or None,
            web_proxy=config.tools.web.proxy or None,
            exec_config=config.tools.exec,
            cron_service=cron,
            restrict_to_workspace=config.tools.restrict_to_workspace,
            session_manager=session_manager,
            mcp_servers=config.tools.mcp_servers,
            channels_config=config.channels,
        )
        
        # Set cron callback
        async def on_cron_job(job: CronJob) -> str | None:
            from nanobot.agent.tools.cron import CronTool
            from nanobot.agent.tools.message import MessageTool
            reminder_note = (
                "[Scheduled Task] Timer finished.\n\n"
                f"Task '{job.name}' has been triggered.\n"
                f"Scheduled instruction: {job.payload.message}"
            )
            
            cron_tool = agent.tools.get("cron")
            cron_token = None
            if isinstance(cron_tool, CronTool):
                cron_token = cron_tool.set_cron_context(True)
            try:
                response = await agent.process_direct(
                    reminder_note,
                    session_key=f"cron:{job.id}",
                    channel=job.payload.channel or "cli",
                    chat_id=job.payload.to or "direct",
                )
            finally:
                if isinstance(cron_tool, CronTool) and cron_token is not None:
                    cron_tool.reset_cron_context(cron_token)
            
            message_tool = agent.tools.get("message")
            if isinstance(message_tool, MessageTool) and message_tool._sent_in_turn:
                return response
            
            if job.payload.deliver and job.payload.to and response:
                from nanobot.bus.events import OutboundMessage
                await bus.publish_outbound(OutboundMessage(
                    channel=job.payload.channel or "cli",
                    chat_id=job.payload.to,
                    content=response
                ))
            return response
        
        cron.on_job = on_cron_job
        
        # Create channel manager
        channels = ChannelManager(config, bus)
        
        def _pick_heartbeat_target() -> tuple[str, str]:
            enabled = set(channels.enabled_channels)
            for item in session_manager.list_sessions():
                key = item.get("key") or ""
                if ":" not in key:
                    continue
                channel, chat_id = key.split(":", 1)
                if channel in {"cli", "system"}:
                    continue
                if channel in enabled and chat_id:
                    return channel, chat_id
            return "cli", "direct"
        
        # Create heartbeat service
        async def on_heartbeat_execute(tasks: str) -> str:
            channel, chat_id = _pick_heartbeat_target()
            async def _silent(*_args, **_kwargs):
                pass
            return await agent.process_direct(
                tasks,
                session_key="heartbeat",
                channel=channel,
                chat_id=chat_id,
                on_progress=_silent,
            )
        
        async def on_heartbeat_notify(response: str) -> None:
            from nanobot.bus.events import OutboundMessage
            channel, chat_id = _pick_heartbeat_target()
            if channel == "cli":
                return
            await bus.publish_outbound(OutboundMessage(channel=channel, chat_id=chat_id, content=response))
        
        hb_cfg = config.gateway.heartbeat
        heartbeat = HeartbeatService(
            workspace=config.workspace_path,
            provider=provider,
            model=agent.model,
            on_execute=on_heartbeat_execute,
            on_notify=on_heartbeat_notify,
            interval_s=hb_cfg.interval_s,
            enabled=hb_cfg.enabled,
        )
        
        if channels.enabled_channels:
            print(f"✓ Channels enabled: {', '.join(channels.enabled_channels)}")
        else:
            print("⚠ Warning: No channels enabled")
        
        cron_status = cron.status()
        if cron_status["jobs"] > 0:
            print(f"✓ Cron: {cron_status['jobs']} scheduled jobs")
        
        print(f"✓ Heartbeat: every {hb_cfg.interval_s}s")
        print(f"✓ Gateway ready!")
        
        # Run everything
        await cron.start()
        await heartbeat.start()
        await asyncio.gather(
            agent.run(),
            channels.start_all(),
        )
        
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        if agent:
            await agent.close_mcp()
            agent.stop()
        if heartbeat:
            heartbeat.stop()
        if cron:
            cron.stop()
        if channels:
            await channels.stop_all()
        await http_runner.cleanup()


if __name__ == "__main__":
    asyncio.run(run_gateway())

# Made with Bob
