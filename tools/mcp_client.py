import asyncio
import os
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack


class JarvisMCPManager:
    def __init__(self):
        self.session = None
        self.exit_stack = None
        self.mcp_tools = []
        self.loop = None  # Holds the explicit running loop instance

    async def connect_to_server(self):
        """Spawns the official open-source filesystem MCP server using stdio transport."""
        # Capture the active event loop running the app right now
        self.loop = asyncio.get_running_loop()

        project_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

        # Target node explicitly, running the package directly via its raw initialization command
        server_params = StdioServerParameters(
            command="npx.cmd",
            args=[
                "--yes",  # <─── CRITICAL: Forces npx to auto-approve the download
                "@modelcontextprotocol/server-filesystem",
                project_dir
            ]
        )

        print(f"[MCP] Initializing connection to filesystem server over path: {project_dir}")

        self.exit_stack = AsyncExitStack()

        read_stream, write_stream = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )

        self.session = await self.exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )
        await self.session.initialize()

        response = await self.session.list_tools()
        self.mcp_tools = response.tools
        print(f"[MCP] Connected! Successfully mounted {len(self.mcp_tools)} dynamic tools from server.")

    def get_gemini_declarations(self) -> list:
        """Translates MCP tools into Gemini FunctionDeclarations on-the-fly."""
        declarations = []
        for tool in self.mcp_tools:
            schema = tool.inputSchema if hasattr(tool, "inputSchema") else {}
            if isinstance(schema, dict):
                schema = dict(schema)
                # ─── THE CRITICAL CLEANUP LINE ──────────────────────────────────
                # Remove the draft schema metadata key that causes Pydantic to crash
                schema.pop("$schema", None)
                # ────────────────────────────────────────────────────────────────

            decl = types.FunctionDeclaration(
                name=tool.name,
                description=tool.description,
                parameters=schema
            )
            declarations.append(decl)
        return declarations

    async def call_mcp_tool(self, name: str, arguments: dict) -> str:
        """Routes tool invocation smoothly onto the target initialization loop thread."""
        if not self.session:
            return "MCP connection session is currently offline."

        try:
            # If the current thread loop differs from the initialization loop, schedule it safely
            current_loop = asyncio.get_running_loop()
            if current_loop != self.loop:
                coro = self.session.call_tool(name, arguments)
                future = asyncio.run_coroutine_threadsafe(coro, self.loop)
                # Wrap the concurrent future to safely await it non-blockingly here
                result = await asyncio.wrap_future(future)
            else:
                result = await self.session.call_tool(name, arguments)

            text_outputs = [content.text for content in result.content if hasattr(content, "text")]
            return "\n".join(text_outputs)
        except Exception as e:
            return f"MCP execution error: {str(e)}"

    async def disconnect(self):
        """Gracefully closes background execution streams."""
        if self.exit_stack:
            await self.exit_stack.aclose()