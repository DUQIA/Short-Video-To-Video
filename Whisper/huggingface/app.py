import torch
import numpy as np
import gradio as gr
from datasets import load_dataset
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model_id = "openai/whisper-large-v3"

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model = model.to_bettertransformer()
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    max_new_tokens=128,
    chunk_length_s=30,
    batch_size=16,
    return_timestamps=True,
    torch_dtype=torch_dtype,
    device=device,
)

dataset = load_dataset("distil-whisper/librispeech_long", "clean", split="validation")
sample = dataset[0]["audio"]

result = pipe(sample)
print(result["text"])

def input(audio):
    if audio is None:
        raise gr.Error("No audio file submitted!")
    
    sr, y = audio
    y = y.astype(np.float32)
    y /= np.max(np.abs(y))
    duration = len(y) / sr

    if duration > 20:
        raise gr.Error("Exceed maximum limit!")
    elif y.ndim != 1:
        raise gr.Error("Please use mono!")
    
    text = pipe({"sampling_rate": sr, "raw": y}, generate_kwargs={"task": "transcribe"}, return_timestamps=True)
    return text["chunks"]

with gr.Blocks() as demo:
    gr.Interface(
                fn=input, 
                inputs="audio", 
                outputs="text", 
                title="Whisper Large V3: Short Audio Timestamp Transcribe", 
                description="🤗 [whisper-large-v3](https://huggingface.co/spaces/hf-audio/whisper-large-v3), Limited the audio length to 20 seconds."
            )

demo.launch()