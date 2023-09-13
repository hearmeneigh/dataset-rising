from typing import Optional

from PIL import Image

from database.entities.post import PostEntity


def resize_image(im: Image.Image, post: PostEntity, max_width: int, max_height: int) -> Optional[Image.Image]:
    try:
        if im.width > max_width or im.height > max_height:
            im.thumbnail((max_width, max_height), resample=Image.LANCZOS, reducing_gap=3.0)

        return im

    except Exception as e:
        print(f'Could not resize image #{post.source_id} ({post.image_url}) - skipping: {str(e)}')
        return None
