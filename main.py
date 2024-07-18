from fastapi import FastAPI
import subprocess

app = FastAPI()

@app.post("/verify-signature/")
async def verify_signature(hash_value: str, signature: str):
    process = await subprocess.create_subprocess_shell(
        command=f"python EncryptionHardwarePort.py verify {hash_value} {signature}",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    stdout, stderr = await process.communicate()
    if process.returncode == 0:
        result = stdout.decode().strip()
        return {"message": result}
    else:
        raise Exception(stderr.decode())

# 运行 Uvicorn 服务器
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)