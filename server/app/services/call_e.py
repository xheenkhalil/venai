import asyncio
import json
import logging
import os

logger = logging.getLogger(__name__)

class CallEService:
    @staticmethod
    async def start_call(phone: str, goal: str) -> dict:
        """Starts a call using the calle CLI and returns the run_id."""
        import shutil
        calle_exec = shutil.which("calle") or "calle.cmd"
        cmd = [
            calle_exec, "call", "start", 
            "--timeout-seconds", "120",
            "--to-phone", phone, 
            "--goal", goal, 
            "--json"
        ]
        
        env = {
            "CALLE_SOURCE": "skills_sh",
            "CALLE_INTEGRATION": "skills_sh_skill",
            "CALLE_INTEGRATION_VERSION": "0.1.0"
        }
        merged_env = os.environ.copy()
        merged_env.update(env)
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=merged_env
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"CALL-E start failed: {stderr.decode()}")
            raise Exception(f"CALL-E start failed: {stderr.decode()}")
            
        try:
            return json.loads(stdout.decode())
        except Exception as e:
            logger.error(f"Failed to parse CALL-E output: {stdout.decode()}")
            raise Exception("Invalid JSON from CALL-E")

    @staticmethod
    async def get_call_status(run_id: str) -> dict:
        """Polls the status of a call run."""
        import shutil
        calle_exec = shutil.which("calle") or "calle.cmd"
        cmd = [
            calle_exec, "call", "status",
            "--timeout-seconds", "120",
            "--run-id", run_id,
            "--json"
        ]
        
        env = {
            "CALLE_SOURCE": "skills_sh",
            "CALLE_INTEGRATION": "skills_sh_skill",
            "CALLE_INTEGRATION_VERSION": "0.1.0"
        }
        merged_env = os.environ.copy()
        merged_env.update(env)
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=merged_env
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"CALL-E status failed: {stderr.decode()}")
            raise Exception(f"CALL-E status failed: {stderr.decode()}")
            
        try:
            return json.loads(stdout.decode())
        except Exception as e:
            logger.error(f"Failed to parse CALL-E status output: {stdout.decode()}")
            raise Exception("Invalid JSON from CALL-E")
