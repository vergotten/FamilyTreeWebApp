from datetime import datetime


def handle_file_upload(file):
    def allowed_file(filename):
        ALLOWED_EXTENSIONS = {'jpg', 'png', 'jpeg', 'gif', 'JPG', 'JPEG'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Get the current script's directory
        script_dir = os.path.dirname(os.path.realpath(__file__))
        # Join it with your desired relative path
        filepath = os.path.join(script_dir, 'static/uploads', filename); print(f"filepath: {filepath}")
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        return os.path.join('uploads', filename)  # return only the relative path

    return None

def get_choices(persons, selected_person):
    if persons is not None:
        choices = [(p.id, p.name) for p in persons]
        if selected_person is not None and (selected_person.id, selected_person.name) in choices:
            choices.remove((selected_person.id, selected_person.name))
            choices.insert(0, (None, ''))
            choices.insert(0, (selected_person.id, selected_person.name))
        else:
            choices.insert(0, (None, ''))
        return choices

def calculate_age(birth_date, death_date=None):
    today = datetime.today().date()  # Get the current date
    age = today.year - birth_date.year

    # if birthday hasn't happened this year, subtract 1
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1

    if death_date is not None:
        age_at_death = death_date.year - birth_date.year
        if (death_date.month, death_date.day) < (birth_date.month, birth_date.day):
            age_at_death -= 1
        return age_at_death, False

    return age, True

def set_person_attributes(person, form, filepath=None):
    person.name = form.name.data or None
    if filepath:
        person.image_file = filepath
    person.birth_date = form.birth_date.data or None
    person.is_alive = form.is_alive.data
    person.death_date = form.death_date.data or None
    person.place_of_live = form.place_of_live.data or None
    person.place_of_birth = form.place_of_birth.data or None
    person.gender = form.gender.data or None
    person.comment = form.comment.data or None