"""
    content images
"""

import io
import os

import zoom
from zoom.buckets import Bucket


css = zoom.load('views/images.css')


class SystemImage(zoom.Record):
    pass


Image = SystemImage


def image_response(name, data):
    """provide an image response based on the file extension"""
    _, ext = os.path.splitext(name.lower())
    if ext == '.png':
        return zoom.response.PNGResponse(data)
    elif ext == '.jpg':
        return zoom.response.JPGResponse(data)
    elif ext == '.gif':
        return zoom.response.GIFResponse(data)

def get_fields():
    return zoom.fields.Fields(
        zoom.fields.ImagesField('Images'),
        zoom.fields.ButtonField('Done'),
    )

def get_edit_form():
    return zoom.forms.form_for(
        zoom.fields.ImagesField('Images'),
        zoom.fields.ButtonField('Save', cancel='/content/images')
    )

class ImageManager(zoom.Controller):

    def index(self):
        """Show all images"""

        actions = 'edit',

        images = zoom.store.store_of(Image)
        t = [dict(
            name=a.image_name,
            size=a.image_size,
            item_id=a.image_id,
            url=zoom.helpers.url_for_page('images', 'get-image', item_id=a.image_id),
        ) for a in images]

        tpl = """
        <a href="/content/images/get-image?item_id={image.image_id}">
        <img class="images-thumbnail" src="/content/images/get-image?item_id={image.image_id}">
        <a>
        """

        content = ''.join(
            tpl.format(image=image)
            for image in images
        )

        css = """
        .images-thumbnail { height: 150px; padding: 0; margin: 0; }
        """

        return zoom.page(
            content,
            title='Images',
            subtitle='Click image to view and copy URL',
            actions=actions,
            css=css,
        )

    def edit(self):
        css = """
        .field_label { display: none; }
        .images-field, .field_edit { width: 100%; }
        .content .transparent { width: 100%; }
        .field_edit .images-field .dropzone { width: 100%; display: table; min-height: 300px; }
        .dropzone .dz-message { margin-top: 140px; }
        """
        content = zoom.forms.form_for(get_fields())
        return zoom.page(content, title='Edit Images', css=css)

    # def show(self):
    #     content = zoom.forms.Form(get_fields()).display_value()
    #     return zoom.page(content, title='Images')

    def cancel(self):
        return zoom.home()

    def clear(self):
        """delete draft images"""
        images = zoom.store.store_of(Image)
        images.delete(draft=True)
        return zoom.page('draft images cleared')

    def done_button(self, key, **data):
        return zoom.home('images')

    def list_images(self, key=None, value=None):
        """return list of images"""
        images = zoom.store.store_of(Image)
        t = [dict(
            name=a.image_name,
            size=a.image_size,
            item_id=a.image_id,
            url=zoom.helpers.url_for('get-image', item_id=a.image_id),
        ) for a in images]
        return zoom.jsonz.dumps(t)

    def get_image(self, *a, **kwargs):  # pylint: disable=W0613
        """return one of the images"""
        item_id = kwargs.get('item_id', None)
        path = os.path.join(zoom.system.site.data_path, 'buckets')
        bucket = Bucket(path)
        return image_response('house.png', bucket.get(item_id))

    def show(self, key):
        path = os.path.join(zoom.system.site.data_path, 'buckets')
        bucket = Bucket(path)
        return image_response('house.png', bucket.get(key))

    def add_image(self, *_, **kwargs):
        """accept uploaded images and attach them to the record"""

        dummy = zoom.Record(
            filename='dummy.png',
            file=io.StringIO('test'),
        )

        # put the uploaded image data in a bucket
        path = os.path.join(zoom.system.site.data_path, 'buckets')
        bucket = Bucket(path)
        f = kwargs.get('file', dummy)
        name = f.filename
        data = f.file.read()
        item_id = bucket.put(data)

        # create an image record
        image = Image(
            image_id=item_id,
            image_size=len(data),
            image_name=name,
            draft=True,
        )
        images = zoom.store.store_of(Image)
        images.put(image)

        return item_id

    def remove_image(self, *_, **kwargs):
        """remove a dropzone image"""
        # k contains item_id and filename for file to be removed
        item_id = kwargs.get('id', None)

        # detach the image from the record
        if item_id:
            images = zoom.store.store_of(Image)
            key = images.first(image_id=item_id)
            if key:
                images.delete(key)

            # delete the bucket
            path = os.path.join(zoom.system.site.data_path, 'buckets')
            bucket = Bucket(path)
            if item_id in bucket.keys():
                bucket.delete(item_id)
                return 'ok'
            return 'empty'


main = zoom.dispatch(ImageManager)