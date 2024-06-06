import whisper
from pydub import AudioSegment
import ffmpeg
import os 

model = whisper.load_model("base")


class Transcription:

    def extract_audio(video_file):
        try:
            base_path = os.path.splitext(video_file)[0]
            audio_file  = f"{base_path}.wav"
            ffmpeg.input(video_file).output(audio_file).run()
            return 1, audio_file
        except Exception as e:
            return 2, e

    def thirty_second(input_audio_path):
        try:
            base_path = os.path.splitext(input_audio_path)[0]
            output_audio_path = f"{base_path}_30_seconds.wav"
            audio = AudioSegment.from_wav(input_audio_path)
            audio_duration = len(audio)
            start_time = audio_duration - 30 * 1000
            last_30_seconds = audio[start_time:]
            last_30_seconds.export(output_audio_path, format='wav')
            return 1, output_audio_path
        except Exception as e:
            return 2, e
        

    def transcription( input_audio_path):
        try:
            base_path = os.path.splitext(input_audio_path)[0]
            output_text = f"{base_path}_transcrption.txt"
            result = model.transcribe(input_audio_path, language='en', word_timestamps=True)
        
            with open(output_text, 'w') as f:
                for segment in result['segments']:
                    for word in segment['words']:
                        f.write(f"{word['start']:.2f}s - {word['word']}\n")
                return 1, output_text
        except Exception as e:
            return 2, e
        

    @staticmethod
    def timestamp_to_seconds(timestamp):
        clean_timestamp = ''.join(c for c in timestamp if c.isdigit() or c == '.')
        try:
            return float(clean_timestamp)
        except ValueError:
            return None
        
    def timestamp(transcription_file_path):
        try:
            with open(transcription_file_path, 'r') as file:
                lines = file.readlines()

            if len(lines) < 14:
                return 2, "The file does not have enough lines to find a line that is 14 lines before the last line."
            else:
                last_line = lines[-1].strip()
                last_line_timestamp = last_line.split('s - ')[0].strip()
                x_line = lines[-14].strip()
                x_line_timestamp = x_line.split('s - ')[0].strip()

                # Convert timestamps to seconds
                timestamp = Transcription()
                last_line_seconds = timestamp.timestamp_to_seconds(last_line_timestamp)
                x_line_seconds = timestamp.timestamp_to_seconds(x_line_timestamp)


                # Calculate the difference between timestamps
                if last_line_seconds is not None and x_line_seconds is not None:
                    timestamp_difference = last_line_seconds - x_line_seconds
                else:
                    timestamp_difference = None

                if timestamp_difference is not None:
                    return 1, timestamp_difference
                else:
                    return 2, "Error in timestamp conversion."
        except Exception as e:
            return 2, e

class Final:

    def flow(self, input_video):
        transcript = Transcription
        val, audio_file = transcript.extract_audio(input_video)
        if val ==1:
            val_1, thirty_second_file =transcript.thirty_second(audio_file) 
            if val_1 ==1:
                val_2, transcription_file = transcript.transcription(thirty_second_file)
                if val_2==1:                    
                    value, time = transcript.timestamp(transcription_file_path=transcription_file)
                    return value, time
            else:
                return val_1, thirty_second_file
        else:
            return val , audio_file

