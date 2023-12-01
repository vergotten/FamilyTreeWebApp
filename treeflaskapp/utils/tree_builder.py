class PersonTreeBuilder:
    def __init__(self, persons):
        """
        Initializes the PersonTreeBuilder with a list of persons. It also sets a dummy ID to -1.

        """
        self._persons = persons
        self._dummy_id = -1

    @property
    def persons(self):
        return self._persons

    @property
    def dummy_id(self):
        return self._dummy_id

    def build_persons_data(self, create_dummies=False):
        """
        Builds and returns a list of person data dictionaries. If create_dummies=True it creates dummy parent.

        """
        persons_data = []

        for person in self._persons:
            if create_dummies:
                if self.needs_dummy_parent(person):
                    dummy_parent = self.create_dummy_parent()
                    persons_data.append(dummy_parent)
                    person.father_id = dummy_parent["id"]

            person_data = self.create_person_data(person)
            persons_data.append(person_data)

        return persons_data

    def needs_dummy_parent(self, person):
        """
        Checks if a person needs a dummy parent. Returns True if the person has a spouse and both parents are None.

        """
        try:
            print(f"Checking person {person.id}:")

            # Check if the person has a spouse
            if person.spouse_id in [None, 'None'] or not self.is_valid_id(person.spouse_id):
                print(f"Person {person.id} does not have a spouse or spouse_id is not valid.")
                return False

            # Check if both parents are None
            if person.mother_id not in [None, 'None']:
                print(f"Person {person.id} has a mother or mother_id is not valid.")
                return False
            if person.father_id not in [None, 'None']:
                print(f"Person {person.id} has a father or father_id is not valid.")
                return False

            print(f"Person {person.id} needs a dummy parent.")
            return True
        except AttributeError:
            # Catch attribute errors if the person object does not have the expected attributes
            print(f"Error: The person object does not have the expected attributes. Please check the input data.")
            return False

    def is_valid_id(self, id_value):
        """
        Checks if an ID value is valid (not None and greater than 0). Returns True if valid, False otherwise.

        """
        if id_value in [None, 'None']:
            return False
        try:
            return int(id_value) > 0
        except ValueError:
            return False

    def create_dummy_parent(self):
        """
        Creates a dummy parent dictionary with a unique ID, default image, and no extra information.
        Decrements the dummy ID after creation.

        """
        dummy_parent = {
            'id': self._dummy_id,
            'name': f'Dummy{self._dummy_id}',
            'mother_id': None,
            'father_id': None,
            'img': '/static/images/no-user-photo.png',  # path to a default image
            'partners': [],
            'extra': {
                'age': None,
                'is_alive': False,
                'place_of_live': None,
                'place_of_birth': None,
                'gender': None,
                'comment': None,
                'user_id': None,
                'birth_date': None,
                'death_date': None,
            }
        }
        self._dummy_id -= 1
        return dummy_parent

    @staticmethod
    def create_person_data(person):
        """
        Creates and returns a dictionary of person data from a person object.
        The dictionary includes IDs, name, image, partners, and extra information.

        """
        return {
            'id': person.id,
            'name': person.name,
            'mother_id': person.mother_id if person.mother_id else None,
            'father_id': person.father_id if person.father_id else None,
            'img': "/static/" + person.image_file if person.image_file else None,
            'partners': [person.spouse_id] if person.spouse_id else [],
            'extra': {
                'age': person.age if person.age else None,
                'is_alive': person.is_alive if person.is_alive else False,
                'place_of_live': person.place_of_live if person.place_of_live else None,
                'place_of_birth': person.place_of_birth if person.place_of_birth else None,
                'gender': person.gender if person.gender else None,
                'comment': person.comment if person.comment else None,
                'user_id': person.user_id if person.user_id else None,
                'birth_date': person.birth_date.strftime('%d-%m-%Y') if person.birth_date is not None else None,
                'death_date': person.death_date.strftime('%d-%m-%Y') if person.death_date is not None else None,
            }
        }

    def __repr__(self):
        """
        Returns a string representation of the PersonTreeBuilder instance, showing the number of persons it contains.

        """
        return f'<PersonTreeBuilder for {len(self._persons)} persons>'
