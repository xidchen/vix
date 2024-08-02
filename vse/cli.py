import os
import pathlib
import shutil
import subprocess
import sys
sys.path.append("/home/song/Documents/Codes/subtitle-flask-bar/vse/")
import rapid_videocr
import utils
from det import SubtitleDetector

def extract_subtitles(path=None,out_path=None,files_th=0) -> None:
    input_sfx = ".mp4"
    output_sfx = ".srt"
    vsf_sub_frame_length = 6
    # vsf_top_video_image_percent_end = 0.36
    # vsf_bottom_video_image_percent_end = 0.24
    # vsf_left_video_image_percent_end = 0.01
    # vsf_right_video_image_percent_end = 0.99
    vsf_dir = "/home/song/Downloads/VideoSubFinder_6.10_ubu20.04/VideoSubFinder"
    vsf_exe_path = "./VideoSubFinderWXW.run"
    root_dir = os.getcwd()
    input_dir = os.path.join(path,'videos')
    output_dir = os.path.join(path, out_path)
    temp_storage_dir = os.path.join(root_dir, "temp_storage")

    if not os.path.exists(input_dir):
        print(f"Input directory {input_dir} does not exist.")
        sys.exit(1)
    if not os.path.exists(output_dir):
        print(f"Create output directory {output_dir}.")
        os.makedirs(output_dir)
    for video_dir, _, video_names in os.walk(input_dir):
        srt_dir = video_dir.replace(input_dir, output_dir)
        for video_name in video_names:
            files_th+=1
            if video_name.endswith(input_sfx):
                video_path = os.path.join(video_dir, video_name)
                srt_name = video_name.replace(input_sfx, output_sfx)
                srt_path = os.path.join(srt_dir, srt_name)
                if not os.path.exists(srt_dir):
                    os.makedirs(srt_dir)
                if os.path.exists(temp_storage_dir):
                    shutil.rmtree(temp_storage_dir)
                os.makedirs(temp_storage_dir)
                os.chdir(vsf_dir)
                detector = SubtitleDetector(video_path, begin_t=None, end_t=None)
                _,subtitle_precent = detector.detect()
                subprocess.run(
                    [vsf_exe_path, "-c", "-r",
                     "-i", video_path,
                     "-o", temp_storage_dir,
                     "-sub_frame_length", f"{vsf_sub_frame_length}",
                     "-te", f"{1-subtitle_precent[0]}",
                     "-be", f"{1-subtitle_precent[1]}",
                     "-le", f"{subtitle_precent[2]}",
                     "-re", f"{subtitle_precent[3]}"]
                )
                os.chdir(root_dir)
                extractor = rapid_videocr.RapidVideOCR(out_format="srt")
                tmp_rgb_dir = os.path.join(temp_storage_dir, "RGBImages")
                for tmp_rgb_name in os.listdir(tmp_rgb_dir):
                    if '-' in tmp_rgb_name:
                        os.remove(os.path.join(tmp_rgb_dir, tmp_rgb_name))
                extractor(
                    video_sub_finder_dir=tmp_rgb_dir,
                    save_dir=srt_dir,
                    save_name=pathlib.Path(srt_name).stem
                )
                shutil.rmtree(temp_storage_dir)
                input_file_path = utils.last_two_levels(video_path)
                output_file_path = utils.last_two_levels(srt_path)
                print(f"{input_file_path} -> {output_file_path}")


if __name__ == "__main__":
    extract_subtitles()
