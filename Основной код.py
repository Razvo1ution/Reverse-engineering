# Импортируем необходимые библиотеки
from colorama import Fore
from colorama import init
from moviepy.editor import (VideoFileClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips)
import os
import sys
import time
from dataclasses import dataclass
from time_range import range_random

# Инициализируем библиотеку colorama
init()

# Определяем рабочую директорию
working_dir = os.path.sep.join(sys.argv[0].split(os.path.sep)[:-1])

# Определяем класс VideoEditor
@dataclass
class VideoEditor:
    path_video: str  # Путь к видеофайлу
    path_audio: str  # Путь к аудиофайлу
    path_directory: str  # Путь к директории с видеофайлами
    path_futage: str  # Путь к футажу
    result_name: str  # Имя результирующего файла
    resolution_selection: str  # Выбранное разрешение

    # Метод для вырезки фрагментов видео
    def video_cut(self) -> None:
        # Проверяем, является ли файл видеофайлом
        if (os.path.split(self.path_video)[-1].endswith(".mp4") or os.path.split(self.path_video)[-1].endswith(".avi")):
            print(Fore.CYAN + '[+] Начинаю вырезку фрагмента видео')
            # Создаем директорию, если она не существует
            output_dir = os.path.join(working_dir, 'media')
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            # Вырезаем фрагменты видео
            for i, (start_time, end_time) in enumerate(range_random()):
                clip = VideoFileClip(self.path_video)
                clip_clip = clip.subclip(start_time, end_time)
                print(Fore.CYAN + '[+] Записываю фрагмент видео...\n')
                clip_clip.write_videofile(f'{working_dir}\\media\\clip_{i}.mp4', codec='libx264', audio=False)
                clip.reader.close()
                clip.audio.reader.close_proc()
            print(Fore.GREEN + '\n[+] Видео успешно сохранены')

    # Метод для объединения видеофайлов
    def video_merge(self) -> None:
        # Проверяем, существует ли директория
        if os.path.exists(self.path_directory):
            print(Fore.CYAN + '[+] Сканирование директории')
            # Получаем список файлов в директории
            clip_in_dir = os.listdir(self.path_directory)
            clip_to_merge = []
            # Фильтруем видеофайлы
            for clip in clip_in_dir:
                if clip.endswith(".mp4") or clip.endswith(".avi"):
                    VideoFileClip(os.path.join(self.path_directory, clip))
                    clip_to_merge.append(VideoFileClip(os.path.join(self.path_directory, clip)))
            # Проверяем, есть ли файлы для объединения
            if len(clip_to_merge) <= 1:
                print(Fore.RED + '[-] В указанной директории нечего объединять')
            else:
                print(Fore.YELLOW + f'[+] Найдено файлов: {len(clip_to_merge)}')
                # Объединяем видеофайлы
                merge_final = concatenate_videoclips(clip_to_merge, method='compose')
                print(Fore.YELLOW + (f'[+] Длительность объединяемого видео: {time.strftime("%H:%M:%S", time.gmtime(merge_final.duration))}' f'\n[+] Начинаю объединение файлов...\n'))
                merge_final.write_videofile(f'{self.result_name}.mp4', codec='libx264', audio=False)
                print(Fore.GREEN + '\n[+] Объединение файлов завершено')
                print(Fore.GREEN + f'[+] Видео {self.result_name}.mp4 сохранено')

    # Метод для добавления футажа
    def add_fx(self) -> None:
            def add_fx(self) -> None:
        print(Fore.LIGHTMAGENTA_EX + '[+] Добавляем футаж')

        video = VideoFileClip(f'{self.result_name}.mp4')
        futage = VideoFileClip(
            self.path_futage).set_duration(video.duration).set_opacity(0.5)
        video_with_futage = CompositeVideoClip([video, futage])
        video_with_futage.write_videofile(f'{self.result_name}_fx.mp4')
        os.remove(f'{self.result_name}.mp4')

    # Метод для генерации полного видео
    def full_video_generation(self) -> None:
        print(Fore.LIGHTMAGENTA_EX + '[+] Генерируем видео и добавляем аудио')
        video_path = f'{working_dir}\\{self.result_name}_fx.mp4'
        audio_path = self.path_audio
        output_path = f'{working_dir}\\{self.result_name}.mp4'
        # Загружаем видеофайл
        video_clip = VideoFileClip(video_path)
        # Загружаем аудиофайл
        audio_clip = AudioFileClip(audio_path)
        # Получаем длительность видео и аудио
        video_duration = video_clip.duration
        audio_duration = audio_clip.duration
        # Вычисляем количество повторений видео, чтобы оно было не короче аудио
        num_repeats = int(audio_duration / video_duration)
        # Зацикливаем видео
        looped_video_clips = [video_clip] * num_repeats
        # Вычисляем остаточную длительность видео для последнего повторения
        remaining_duration = audio_duration - (num_repeats * video_duration)
        if remaining_duration > 0:
            # Создаем последний клип с остаточной длительностью
            last_clip = video_clip.subclip(0, remaining_duration)
            looped_video_clips.append(last_clip)
        # Объединяем зацикленные клипы
        final_video_clip = concatenate_videoclips(looped_video_clips)
        # Изменяем разрешение, если необходимо
        new_resolution = (1440, 1080)
        if self.resolution_selection == 'y':
            final_video_clip = final_video_clip.resize(new_resolution)
            print(Fore.LIGHTMAGENTA_EX + (f'\nРазрешение изменено на {new_resolution}.'))
        else:
            print(Fore.LIGHTMAGENTA_EX + '\nРазрешение оставлено без изменений.')
        # Добавляем аудиодорожку к видео
        final_clip = final_video_clip.set_audio(audio_clip)
        # Записываем видео на диск
        final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
        # Закрываем файлы
        video_clip.reader.close()
        video_clip.audio.reader.close_proc()
        os.remove(f'{self.result_name}_fx.mp4')
    # Управляет процессом видеоредактирования, используя введенные пользователем данные и вызывая соответствующие методы объекта VideoEditor.
    def main() -> None:
        video = VideoEditor(
            input(Fore.LIGHTMAGENTA_EX + '(Пример: '
                                         'C:\\desktop\\video\\video.mp4)\n'
                                         'Введите полный путь видеофайла: '),
            input(Fore.LIGHTMAGENTA_EX + '(Пример: '
                                         'C:\\desktop\\music\\song.mp3)\n'
                                         'Введите полный путь аудиофайла: '),
            os.path.join(working_dir, 'media'),
            f'{working_dir}\\futage.mp4',
            input('Введите название нового видео: '),
            input(
                "Желаете изменить разрешение видео на 1440x1080? (Y/N): ").lower()
        )
        video.video_cut()
        video.video_merge()
        video.add_fx()
        video.full_video_generation()


if __name__ == "__main__":
    main()