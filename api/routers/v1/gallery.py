from fastapi import APIRouter, Depends
from deps import get_current_admin
from apps.careers.models import GalleryItem

router = APIRouter()


@router.get('')
def list_gallery():
    return [{
        'id': item.id, 'title': item.title, 'image_url': item.image_url,
        'alt_text': item.alt_text, 'caption': item.caption,
    } for item in GalleryItem.objects.filter(is_active=True).order_by('sort_order', '-created_at')[:200]]


@router.post('', status_code=201)
def create_gallery_item(
    title: str,
    image_url: str,
    alt_text: str = '',
    caption: str = '',
    sort_order: int = 0,
    admin=Depends(get_current_admin),
):
    item = GalleryItem.objects.create(
        title=title, image_url=image_url, alt_text=alt_text,
        caption=caption, sort_order=max(0, sort_order),
    )
    return {'id': item.id, 'message': 'تصویر گالری ثبت شد'}
