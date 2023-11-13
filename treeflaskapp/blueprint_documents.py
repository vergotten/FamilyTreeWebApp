from flask import Blueprint, request, render_template, redirect, url_for, g, flash, jsonify, current_app
from flask_login import login_required, current_user
from .models import Document, File, Person, Place, Event, db
from .forms import DocumentForm, FileForm
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
            ALLOWED_EXTENSIONS = None  # allow all extensions
        return '.' in filename and (
                    ALLOWED_EXTENSIONS is None or filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS)

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
@login_required
def documents_view(username):
    if username == current_user.username:
        documents = Document.query.filter_by(user_id=current_user.id).all()
        form = DocumentForm(user_language=g.user_language)  # create an instance of your DocumentForm
        file_form = FileForm(user_language=g.user_language)  # create an instance of your FileForm
        return render_template('documents.html', documents=documents, form=form, file_form=file_form)
    else:
        return "Unauthorized", 403

@documents.route('/user/<username>/create_document', methods=['GET', 'POST'])
@login_required
def create_document(username):
    form = DocumentForm(user_language=g.user_language)
    file_form = FileForm(user_language=g.user_language)
    if form.validate_on_submit():
        try:
            icon_path = None
            if 'icon' in request.files and request.files['icon'].filename != '':
                icon_path = handle_file_upload(request.files['icon'], is_image=True, id=current_user.id)

            document = Document(user_id=current_user.id,
                                name=form.name.data,
                                description=form.description.data if form.description.data else None,
                                date=form.date.data if form.date.data else None,
                                comment=form.comment.data if form.comment.data else None,
                                icon=icon_path if icon_path else None)
            db.session.add(document)
            db.session.commit()

            if 'file_path' in request.files:
                for file in request.files.getlist('file_path'):
                    if file.filename != '':
                        file_path = handle_file_upload(file, is_image=False, id=current_user.id)
                        file = File(file_path=file_path, document_id=document.id)
                        db.session.add(file)

            db.session.commit()
            flash_message = 'Document created successfully!' if g.user_language == 'en' else 'Документ успешно создан!'
            flash(flash_message, 'success')
            return redirect(url_for('documents.documents_view', username=username))
        except Exception as e:
            db.session.rollback()
            flash_message = 'An error occurred while creating the document: {}'.format(e) if g.user_language == 'en' \
                else 'Произошла ошибка при создании документа: {}'.format(e)
            flash(flash_message, 'error')
    return render_template('create_document.html', form=form, file_form=file_form, username=username)

@documents.route('/user/<username>/edit_document/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_document(username, id):
    document = Document.query.get(id)
    if document is None or document.user_id != current_user.id:
        abort(403)

    form = DocumentForm(obj=document, user_language=g.user_language)
    file_form = FileForm(user_language=g.user_language)
    if form.validate_on_submit():
        try:
            if 'icon' in request.files and request.files['icon'].filename != '':
                icon_path = handle_file_upload(request.files['icon'], is_image=True, id=current_user.id)
                document.icon = icon_path  # update image_file field with full path

            document.name = form.name.data if form.name.data else None
            document.description = form.description.data if form.description.data else None
            document.date = form.date.data if form.date.data else None
            document.comment = form.comment.data if form.comment.data else None

            if 'file_path' in request.files:
                for file in request.files.getlist('file_path'):
                    if file.filename != '':
                        file_path = handle_file_upload(file, is_image=False, id=current_user.id)
                        file = File(file_path=file_path, document_id=document.id)
                        db.session.add(file)

            db.session.commit()
            flash_message = 'Document updated successfully!' if g.user_language == 'en' else 'Документ успешно обновлен!'
            flash(flash_message, 'success')
            return redirect(url_for('documents.documents_view', username=username))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the document: {}'.format(e), 'error')

    return render_template('edit_document.html', form=form, file_form=file_form, username=username, document=document)


@documents.route('/user/<username>/delete_document/<int:id>', methods=['POST'])
@login_required
def delete_document(username, id):
    document = Document.query.get(id)
    if document is None or document.user_id != current_user.id:
        return "Unauthorized", 403

    try:
        if document.icon:
            # If the document's icon is the same as the filename, set it to None
            file_path = os.path.join(current_app.root_path, 'static', document.icon);

            if os.path.exists(file_path):
                os.remove(file_path)

            document.icon = None
            db.session.commit()

        # Delete the files associated with the document
        for file in document.files:
            # Construct the full file path
            file_path = os.path.join(current_app.root_path, 'static', file.file_path)
            # Check if the file exists and delete it
            if os.path.exists(file_path):
                os.remove(file_path)
            # Delete the file record from the database
            db.session.delete(file)

        # Delete the document
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
    filename = data.get('filename'); print(f"filename: {filename}")
    file_path = data.get('file_path'); print(f"file_path: {file_path}")

    if filename or file_path:
        document = Document.query.get(id)
        if document:
            if document.icon == filename and filename is not None and filename != "":
                # If the document's icon is the same as the filename, set it to None
                file_path = os.path.join(current_app.root_path, 'static', filename);

                if os.path.exists(file_path):
                    os.remove(file_path)

                document.icon = None
                db.session.commit()

            file_to_delete = None
            for file in document.files:
                if file.file_path == file_path:
                    file_to_delete = file
                    break

            if file_to_delete:
                # If the document's file path is the same as the filename, set it to None
                file_path = os.path.join(current_app.root_path, 'static', file_path); print(f"file_path: {file_path}")

                if os.path.exists(file_path):
                    os.remove(file_path)

                db.session.delete(file_to_delete)
                db.session.commit()

                return jsonify({'message': 'File deleted.', 'success': True}), 200
        else:
            return jsonify({'message': 'Document not found.'}), 404
    else:
        return jsonify({'message': 'No filename provided.'}), 400
