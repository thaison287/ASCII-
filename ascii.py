import os
import math
import tempfile
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, ImageSequenceClip

# ==========================
# Cấu hình ký tự ASCII
# ==========================
chars = "@#W$9876543210?!abc;:+=-,._ "[::-1]  # Ký tự từ đậm đến nhạt  
charArray = list(chars)
charLength = len(charArray)
interval = charLength / 256

scaleFactor = 0.3
oneCharWidth = 8
oneCharHeight = 15

# ==========================
# Hàm hỗ trợ
# ==========================
def getChar(inputInt):
    return charArray[math.floor(inputInt * interval)]

def load_font():
    """Tự động chọn font có sẵn trong Windows"""
    font_path = "C:\\Windows\\Fonts\\lucon.ttf"
    if not os.path.exists(font_path):
        font_path = "C:\\Windows\\Fonts\\consola.ttf"
    return ImageFont.truetype(font_path, 14)

# ==========================
# Chuyển ảnh sang ASCII
# ==========================
def image_to_ascii_frame(img, font, draw_color=True):
    width, height = img.size
    img = img.resize(
        (
            int(scaleFactor * width),
            int(scaleFactor * height * (oneCharWidth / oneCharHeight))
        ),
        Image.NEAREST
    )
    width, height = img.size

    outputImage = Image.new("RGB", (oneCharWidth * width, oneCharHeight * height), color=(0, 0, 0))
    draw = ImageDraw.Draw(outputImage)

    for i in range(height):
        for j in range(width):
            r, g, b = img.getpixel((j, i))
            h = int((r + g + b) / 3)
            pixelChar = getChar(h)
            if draw_color:
                draw.text((j * oneCharWidth, i * oneCharHeight), pixelChar, font=font, fill=(r, g, b))
            else:
                draw.text((j * oneCharWidth, i * oneCharHeight), pixelChar, font=font, fill=(h, h, h))
    return outputImage

# ==========================
# Hàm chuyển frame cho video
# ==========================
def convert_image_to_ascii_image(image):
    font = load_font()
    return image_to_ascii_frame(image, font, draw_color=True)

# ==========================
# Xử lý file ảnh tĩnh
# ==========================
def process_image_file(path):
    print("🖼️ Đang xử lý ảnh tĩnh...")
    font = load_font()
    img = Image.open(path)
    ascii_img = image_to_ascii_frame(img, font)
    ascii_img.save("output_image.png")
    print("✅ Đã lưu ảnh ASCII thành output_image.png")

# ==========================
# Xử lý file GIF
# ==========================
def process_gif_file(path):
    print("🎞️ Đang xử lý ảnh động (GIF)...")
    font = load_font()
    img = Image.open(path)

    frames = []
    for frame in range(img.n_frames):
        img.seek(frame)
        ascii_frame = image_to_ascii_frame(img.copy(), font)
        frames.append(ascii_frame)

    frames[0].save(
        "output_gif.gif",
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=img.info.get("duration", 100)
    )
    print("✅ Đã lưu GIF ASCII thành output_gif.gif")

# ==========================
# Xử lý video (MP4, MOV...)
# ==========================
def process_video_file(filename):
    from moviepy.editor import VideoFileClip, ImageSequenceClip
    import tempfile, shutil

    print("🎬 Đang xử lý video...")

    clip = VideoFileClip(filename)
    audio = clip.audio
    total_frames = int(clip.fps * clip.duration)
    print(f"📸 Tổng số frame: {total_frames}")

    temp_dir = tempfile.mkdtemp()
    ascii_frames = []

    font = ImageFont.truetype("C:\\Windows\\Fonts\\lucon.ttf", 14)

    frame_count = 0
    for frame in clip.iter_frames(fps=clip.fps, dtype="uint8"):
        frame_count += 1
        img = Image.fromarray(frame)
        ascii_img = image_to_ascii_frame(img, font)  # ✅ Gọi đúng hàm chuyển ASCII
        frame_path = os.path.join(temp_dir, f"frame_{frame_count:05d}.png")
        ascii_img.save(frame_path)
        ascii_frames.append(frame_path)

        if frame_count % 10 == 0 or frame_count == total_frames:
            print(f"🧩 Đã xử lý {frame_count}/{total_frames} frame...")

    print("🎞️ Ghép các frame ASCII thành video...")

    # 🧩 Tạo video từ danh sách frame PNG
    ascii_clip = ImageSequenceClip(ascii_frames, fps=clip.fps)

    # 🔊 Thêm lại âm thanh gốc
    if audio:
        ascii_clip = ascii_clip.set_audio(audio)
    else:
        print("⚠️ Video gốc không có âm thanh hoặc không đọc được âm thanh.")

    output_file = "output_ascii.mp4"
    ascii_clip.write_videofile(
        output_file,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="medium",
        fps=clip.fps
    )

    # 🧹 Dọn file tạm
    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"✅ Hoàn thành! Video ASCII đã lưu tại: {output_file}")


# ==========================
# Chương trình chính
# ==========================
def main():
    path = input("📂 Nhập đường dẫn file (.jpg / .png / .gif / .mp4): ").strip('"')

    if not os.path.exists(path):
        print("❌ Không tìm thấy file, vui lòng kiểm tra lại đường dẫn.")
        return

    ext = os.path.splitext(path)[1].lower()
    if ext in [".jpg", ".jpeg", ".png"]:
        process_image_file(path)
    elif ext == ".gif":
        process_gif_file(path)
    elif ext in [".mp4", ".avi", ".mov", ".mkv"]:
        process_video_file(path)
    else:
        print("⚠️ Định dạng không được hỗ trợ.")

if __name__ == "__main__":
    main()
