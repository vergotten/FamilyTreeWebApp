from flask import Blueprint, request, render_template, redirect, url_for, g, flash
from flask_login import login_required, current_user
from .models import Document, Person, Place, Event, db
from .forms import DocumentForm
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from sqlalchemy import and_, or_

documents = Blueprint('documents', __name__)

def handle_file_upload(file, id, is_image=False):
    def allowed_file(filename):
        if is_image:
            ALLOWED_EXTENSIONS = {'jpg', 'png', 'jpeg', 'gif', 'JPG', 'JPEG'}
        else:
            ALLOWED_EXTENSIONS = {'jpg', 'png', 'jpeg', 'gif', 'JPG', 'JPEG', 'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx',
                                  'ppt', 'pptx', 'csv', 'rtf', 'odt', 'ods', 'odp', 'zip', 'rar', 'tar', 'gz',
                                  '7z'}  # добавить другие расширения файлов по мере необходимости
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Get the current script's directory
        script_dir = os.path.dirname(os.path.realpath(__file__))
        # Join it with your desired relative path
        if is_image:
            filepath = os.path.join(script_dir, 'static/uploads/images', str(id), filename)
        else:
            filepath = os.path.join(script_dir, 'static/uploads/documents', str(id), filename)
        print(f"filepath: {filepath}")
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        return os.path.join('uploads', 'images' if is_image else 'documents', str(id), filename)  # return only the relative path

    return None


@documents.route('/user/<username>/documents')
def documents_view(username):
    if username == current_user.username:
        documents = Document.query.filter_by(user_id=current_user.id).all()
        form = DocumentForm(user_language=g.user_language)  # create an instance of your form
        return render_template('documents.html', documents=documents, form=form)
    else:
        return "Unauthorized", 403

@documents.route('/user/<username>/create_document', methods=['GET', 'POST'])
@login_required
def create_document(username):
    form = DocumentForm(user_language=g.user_language)
    if form.validate_on_submit():
        try:
            icon_path = None
            if 'icon' in request.files and request.files['icon'].filename != '':
                icon_path = handle_file_upload(request.files['icon'], is_image=True, id=current_user.id)

            file_path = None
            if 'file_path' in request.files and request.files['file_path'].filename != '':
                file_path = handle_file_upload(request.files['file_path'], is_image=False, id=current_user.id)

            document = Document(user_id=current_user.id,
                                name=form.name.data,
                                description=form.description.data if form.description.data else None,
                                date=form.date.data if form.date.data else None,
                                file_path=file_path,
                                comment=form.comment.data if form.comment.data else None,
                                icon=icon_path if icon_path else None)
            db.session.add(document)
            db.session.commit()
            flash_message = 'Document created successfully!' if g.user_language == 'en' else 'Документ успешно создан!'
            flash(flash_message, 'success')
            return redirect(url_for('documents.documents_view', username=username))
        except Exception as e:
            db.session.rollback()
            flash_message = 'An error occurred while creating the document: {}'.format(e) if g.user_language == 'en' \
                else 'Произошла ошибка при создании документа: {}'.format(e)
            flash(flash_message, 'error')
    return render_template('create_document.html', form=form, username=username)

@documents.route('/user/<username>/edit_document/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_document(username, id):
    document = Document.query.get(id)
    if document is None or document.user_id != current_user.id:
        return "Unauthorized", 403

    form = DocumentForm(obj=document, user_language=g.user_language)
    if form.validate_on_submit():
        try:
            # icon_path = None
            if 'icon' in request.files and request.files['icon'].filename != '':
                icon_path = handle_file_upload(request.files['icon'], is_image=True, id=current_user.id)
                document.icon = icon_path  # update image_file field with full path

            document.name = form.name.data if form.name.data else None
            document.description = form.description.data if form.description.data else None
            document.date = form.date.data if form.date.data else None
            document.file_path = form.file_path.data if form.file_path.data else None
            document.comment = form.comment.data if form.comment.data else None
            # document.icon = form.icon.data if form.icon.data else None

            db.session.commit()
            flash_message = 'Document updated successfully!' if g.user_language == 'en' else 'Документ успешно обновлен!'
            flash(flash_message, 'success')
            return redirect(url_for('documents.documents_view', username=username))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the document: {}'.format(e), 'error')

    return render_template('edit_document.html', form=form, username=username, document=document)

@documents.route('/user/<username>/delete_document/<int:id>', methods=['POST'])
@login_required
def delete_document(username, id):
    document = Document.query.get(id)
    if document is None or document.user_id != current_user.id:
        return "Unauthorized", 403

    try:
        db.session.delete(document)
        db.session.commit()
        flash_message = 'Document deleted successfully!' if g.user_language == 'en' else 'Документ успешно удален!'
        flash(flash_message, 'success')
    except Exception as e:
        db.session.rollback()
        flash_message = 'An error occurred while deleting the document: {}'.format(e) if g.user_language == 'en' \
            else 'Произошла ошибка при удалении документа: {}'.format(e)
        flash(flash_message, 'error')

    return redirect(url_for('documents.documents_view', username=username))

@documents.route('/user/<username>/edit_document/<int:id>/delete-file', methods=['POST'])
@login_required
def delete_file(username, id):
    data = request.get_json()
    filename = data.get('filename')

    print('Received request:', request)  # Print the entire request
    print('Received data:', data)  # Print the received JSON data
    print('Received filename:', filename)  # Print the received filename

    if filename:
        document = Document.query.get(id)
        if document and document.icon == filename:
            # If the person's image_file is the same as the filename, set it to None
            document.icon = None
            db.session.commit()

            file_path = os.path.join(documents.root_path, 'static', filename)

            if os.path.exists(file_path):
                os.remove(file_path)

            return jsonify({'message': 'File deleted.'}), 200
        else:
            return jsonify({'message': 'File not found.'}), 404
    else:
        return jsonify({'message': 'No filename provided.'}), 400