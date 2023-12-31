import re
import os
import ffmpy
import asyncio
import tarfile
import edge_tts
import subprocess
import gradio as gr
import translators as ts
from gradio_client import Client
from requests.exceptions import ConnectionError
from list_dict import translates, speakers

if not os.path.exists('pretrained_models'):
    with tarfile.open('2stems.tar.gz', 'r:gz') as tar_ref:
        tar_ref.extractall('./pretrained_models/2stems')

translate = translates
tr = list(translate.keys())[9]
language = translate[tr]
la = list(language.keys())[0]
speaker = speakers
sp = speaker[0]

max_duration = 60
file_name = 'audio'
main_video = 'video.mp4'
main_audio = f'{file_name}.wav'
folder = 'output_directory'
text_to_speech = 'text_to_speech.wav'
vocals = f'./{folder}/{file_name}/vocals.wav'
vocals_monorail = f'./{folder}/{file_name}/vocals_monorail.wav'
accompaniment = f'./{folder}/{file_name}/accompaniment.wav'
output_left_audio = 'output_left_audio.wav'
output_rate_audio = 'output_rate_audio.wav'
output_audio = 'output.wav'
output_video = 'output.mp4'

def gain_time(audio):
  command = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', audio]
  result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  return float(result.stdout)

def left_justified(audio):
  try:
    command = ['ffmpeg', '-i', audio, '-af', 'silencedetect=n=-38dB:d=0.01', '-f', 'null', '-']
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    start_justified = re.search(r'silence_duration: (\d.\d+)', result.stdout.decode(), re.M|re.S).group(1)
  except AttributeError:
    raise gr.Error('No start sound detected!')
  return start_justified
  
def time_verify(vocals_audio, target_audio):
  audios = [vocals_audio, target_audio]
  justified = []
  time_lists = []

  for audio in audios:
    justified.append(left_justified(audio))
    time_lists.append(gain_time(audio))

  j_time = float(justified[0]) - float(justified[1])

  if float(time_lists[0]) > float(time_lists[1]):
      r_time = float(min(time_lists)) / (float(max(time_lists)) - j_time)
  else:
      r_time = float(max(time_lists)) / float(min(time_lists))
  return round(j_time, 6), round(r_time, 6)

def translator(text, TR_LANGUAGE, LANGUAGE):
  try:
    ts_text = ts.translate_text(text, translator=TR_LANGUAGE, from_language='auto', to_language=language[LANGUAGE])
  except ConnectionError as i:
    raise gr.Error(f'translator ConnectionError:{i}')
  except ts.TranslatorError:
    raise gr.Error('Translator error!')
  return ts_text

def video_inputs(video, TR_LANGUAGE, LANGUAGE, SPEAKER):
  gl = True
  language = translate[TR_LANGUAGE]
  get_time = float(gain_time(video))

  if video is None:
      raise gr.Error('No audio file submitted!')
  elif language is None:
      raise gr.Error('Please select google translator!')
  elif SPEAKER is None:
      raise gr.Error('Please select a Speaker！')
  elif TR_LANGUAGE == tr:
      if gl is False:
          gl = True
          raise gr.Error('Language has been reloaded, please select again!')
  elif TR_LANGUAGE != tr:
      if gl is True:
          gl = False
          raise gr.Error('Language has been reloaded, please select again!')
  elif get_time > max_duration:
      raise gr.Error('Exceed maximum limit!')

  try:
    ff = ffmpy.FFmpeg(
        inputs={
            video: f'-t {max_duration}'
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
          vocals_monorail: ['-y', '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', '-f', 'wav']
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
  except ffmpy.FFRuntimeError:
   raise gr.Error('Mismatched audio!')
  except ConnectionError as e:
    raise gr.Error(f'API:{e}')

  async def amain():
    communicate = edge_tts.Communicate(ts_text, SPEAKER)
    await communicate.save(text_to_speech)
  asyncio.run(amain())

  r_time = time_verify(vocals_monorail, text_to_speech)
  ff = ffmpy.FFmpeg(
      inputs={
          text_to_speech: None
      },
      outputs={
          output_rate_audio: ['-y', '-filter:a', f'atempo={r_time[1]}']
      }
  )
  ff.run()
  j_time = time_verify(vocals_monorail, output_rate_audio)
  if j_time[0] > 0:
      ff = ffmpy.FFmpeg(
          inputs={
              output_rate_audio: None
          },
          outputs={
              output_left_audio: ['-y', '-af', f'areverse,apad=pad_dur={j_time[0]}s,areverse']
          }
      )
      ff.run()
  else:
      ff = ffmpy.FFmpeg(
          inputs={
              output_rate_audio: None
          },
          outputs={
              output_left_audio: ['-y',  '-filter:a', f'atrim=start={abs(j_time[0])}']
          }
      )
      ff.run()

  ff = ffmpy.FFmpeg(
      inputs={
          output_left_audio: None,
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

  return output_video, accompaniment, vocals_monorail, output_left_audio, text_to_speech, result, ts_text

with gr.Blocks() as demo:
  TR_LANGUAGE = gr.Dropdown(translate, value=tr, label='Translator')
  LANGUAGE = gr.Dropdown(language, value=la, label='Language')
  SPEAKER = gr.Dropdown(speaker, value=sp, label='Speaker')
  gr.Interface(
      fn=video_inputs,
      inputs=[
          gr.Video(height=320, interactive=True, label='Input_video'),
          TR_LANGUAGE,
          LANGUAGE,
          SPEAKER,
          ],
      outputs=[
          gr.Video(height=320, label='Output_video'),
          gr.Audio(label='Accompaniment'),
          gr.Audio(label='Vocals'),
          gr.Audio(label='Vocals_justified'),
          gr.Audio(label='Text_speech'),
          gr.Text(label='Original'),
          gr.Text(label='Translation'),
      ],
      title="Short-Video-To-Video", 
      description="🤗 [whisper-large-v3](https://huggingface.co/spaces/hf-audio/whisper-large-v3), Limited the video length to 60 seconds. Currently only supports google Translator, Use other [translators](https://github.com/DUQIA/Short-Video-To-Video/blob/main/README.md#use-other-translators). Please check [here](https://github.com/DUQIA/Short-Video-To-Video) for details."
  )
demo.launch()
