import io
from urllib import response
from fastapi import FastAPI, File
import uvicorn
from starlette.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from style import style_transfer

app = FastAPI()

# 跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
async def root():
    return [{'status': 'ok'}]

@app.post('/style')
async def predict(file: bytes = File(...)):
    stylized_image = style_transfer(io.BytesIO(file))
    stylized_image.seek(0)
    return StreamingResponse(
        stylized_image,
        media_type="image/jpg",
    )

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)