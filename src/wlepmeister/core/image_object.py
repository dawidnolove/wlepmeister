from PIL import Image, ImageTk


class ImageObject:
    def __init__(self, image_path=None, x=0, y=0, pil_image=None):
        self.image_path = image_path
        self.x = x
        self.y = y
        if pil_image is not None:
            self.pil_image = pil_image.convert("RGBA").copy()
        else:
            if not image_path:
                raise ValueError("Image path is required for file import.")
            with Image.open(image_path) as source_image:
                if source_image.format != "PNG":
                    raise ValueError("Only PNG files are allowed.")
                self.pil_image = source_image.convert("RGBA").copy()
        self.photo_image = ImageTk.PhotoImage(self.pil_image)
