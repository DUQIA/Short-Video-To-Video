import ffmpy
import asyncio
import edge_tts
import subprocess
import gradio as gr
import translators as ts
from gradio_client import Client
from list_dict import translates, speakers

translate = translates
language = translate[list(translate.keys())[9]]
speaker = speakers

file_name = 'audio'
main_video = 'video.mp4'
main_audio = f'{file_name}.wav'
folder = 'output_directory'
text_to_speech = 'text_to_speech.wav'
vocals = f'./{folder}/{file_name}/vocals.wav'
vocals_monorail = f'./{folder}/{file_name}/vocals_monorail.wav'
accompaniment = f'./{folder}/{file_name}/accompaniment.wav'
output_rate_audio = 'output_rate_audio.wav'
output_audio = 'output.wav'
output_video = 'output.mp4'

def gain_time(audio):
  command = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', audio]
  result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  return float(result.stdout)

def time_verify():
  audios = [vocals_monorail, text_to_speech]
  time_lists = []

  for audio in audios:
    time_lists.append(gain_time(audio))

  r_time = float(max(time_lists)) / float(min(time_lists))
  return r_time

def translator(text, TR_LANGUAGE, LANGUAGE):
  ts_text = ts.translate_text(text, translator=TR_LANGUAGE, from_language='auto', to_language=language[LANGUAGE])
  return ts_text

def video_inputs(video, TR_LANGUAGE, LANGUAGE, SPEAKER):
  language = translate[TR_LANGUAGE]

  if video is None:
      raise gr.Error('No audio file submitted!')
  elif language is None:
      raise gr.Error('Please select google translator!')
  elif TR_LANGUAGE != 'google':
      raise gr.Error('Language has been reloaded, please select again!')
  elif float(gain_time(video)) > 60:
      raise gr.Error('Exceed maximum limit!')

  ff = ffmpy.FFmpeg(
      inputs={
          video: None
          },
      outputs={
          main_video: ['-y', '-map', '0:0', '-c:a', 'copy', '-f', 'mp4'],
          main_audio: ['-y', '-map', '0:a', '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', '-f', 'wav']
          }
      )
  ff.run()

  subprocess.run(['spleeter', 'separate', '-o', folder, '-p', 'spleeter:2stems-16kHz', main_audio])

  ff = ffmpy.FFmpeg(
      inputs={
          vocals: None
          },
      outputs={
          vocals_monorail: ['-y', '-i', vocals, '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', '-f', 'wav']
          }
      )
  ff.run()

  client = Client('https://hf-audio-whisper-large-v3.hf.space/')
  result = client.predict(
          vocals_monorail,	# str (filepath or URL to file) in 'inputs' Audio component
          'transcribe',	# str in 'Task' Radio component
          api_name='/predict'
  )

  ts_text = translator(result, TR_LANGUAGE, LANGUAGE)

  async def amain():
    communicate = edge_tts.Communicate(ts_text, SPEAKER)
    await communicate.save(text_to_speech)
  asyncio.run(amain())

  rate_audio = time_verify()
  ff = ffmpy.FFmpeg(
      inputs={text_to_speech: None},
      outputs={
          output_rate_audio: ['-y', '-filter:a', f'atempo={rate_audio}']
      }
  )
  ff.run()

  ff = ffmpy.FFmpeg(
      inputs={
          output_rate_audio: None,
          accompaniment: None
      },
      outputs={
          output_audio: '-y -filter_complex amix=inputs=2'
      }
  )
  ff.run()

  ff = ffmpy.FFmpeg(
      inputs={output_audio: None, main_video: None},
      outputs={output_video: '-y -c:v copy -c:a aac -strict experimental'}
  )
  ff.run()

  return output_video

with gr.Blocks() as demo:
  TR_LANGUAGE = gr.Dropdown(translate, value=list(translate.keys())[9], label='Translator')
  LANGUAGE = gr.Dropdown(language, value=list(language.keys())[0], label='Language')
  SPEAKER = gr.Dropdown(speaker, value=speaker[0], label='Speaker')
  gr.Interface(
      fn=video_inputs,
      inputs=[
          gr.Video(height=320, width=600, interactive=True, label='Input_video'),
          TR_LANGUAGE,
          LANGUAGE,
          SPEAKER,
          ],
      outputs=[
          gr.Video(height=320, width=600, label='Output_video'),
      ],
      title="Short-Video-To-Video", 
      description="🤗 [whisper-large-v3](https://huggingface.co/spaces/hf-audio/whisper-large-v3), Limited the video length to 60 seconds. Currently only supports google Translator. Please check [here](https://github.com/DUQIA/Short-Video-To-Video) for details."
  )
demo.launch()