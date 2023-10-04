from io import BytesIO
from typing import Optional

from PIL import Image

from database.entities.post import PostEntity


def load_image(file: bytes, post: PostEntity) -> Optional[Image.Image]:
    try:
        im = Image.open(BytesIO(file))

        return im.convert('RGB')

    except Exception as e:
        print(f'Could not load image #{post.source_id} ({post.image_url}) -- skipping: {str(e)}')
        return None
