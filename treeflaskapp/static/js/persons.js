//import $ from 'jquery';
//import $ from './jquery.js';
//
//import DataTable from './datatables.net';

// Now you can use DataTables
$(document).ready(function() {
    $('#myTable').DataTable();
});


// Create a JavaScript variable for the static URL
var staticUrl = "{{ url_for('static', filename='') }}";
var username = document.getElementById('username').value;

$(document).ready(function(){
    var table = $('#myTable').DataTable({
        pageLength: 10,
        createdRow: function(row, data) {
            $(row).click(function(){
                // Get the img element
                var img = $('.image-container img');

                if ($(this).hasClass('highlight')) {
                    $(this).removeClass('highlight');
                    $('#openBtn, #editBtn, #deleteBtn').prop('disabled', true);

                    // Display the no-user-photo.png image
                    img.attr('src', staticUrl + 'images/no-user-photo.png');
                } else {
                    $('#myTable tbody tr').removeClass('highlight');
                    $(this).addClass('highlight');
                    $('#openBtn, #editBtn, #deleteBtn').prop('disabled', false);

                    // Get the image_file value from the clicked row
                    var imageFile = data[3];  // Access the image_file value by its index

                    // Update the src attribute of the img element
                    if (imageFile && isValidImageFile(imageFile)) {
                        img.attr('src', staticUrl + imageFile);
                        console.log(staticUrl + imageFile);  // Print the image path
                    } else {
                        img.attr('src', staticUrl + 'images/no-user-photo.png');
                        console.log(staticUrl + 'images/no-user-photo.png');  // Print the image path
                    }
                }
            });
        }
    });
});

function isValidImageFile(imageFile) {
    var imageFileExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', 'JPG', 'JPEG'];
    for (var i = 0; i < imageFileExtensions.length; i++) {
        if (imageFile.endsWith(imageFileExtensions[i])) {
            return true;
        }
    }
    return false;
}

function editPerson() {
    var id = $('#myTable tr.highlight').data('id');
    if (id) {
//        var username = '{{ session['username'] }}'; // get username from session
        window.location.href = '/persons/user/' + username + '/edit_person/' + id;
    }
}

function deletePerson() {
    var id = $('#myTable tr.highlight').data('id');
    if (id) {
//        var username = '{{ session['username'] }}'; // get username from session
        $.ajax({
            url: '/persons/user/' + username + '/delete_person/' + id,
            type: 'POST',
            success: function(result) {
                // Remove the deleted record from the table
                $('#myTable tr.highlight').remove();
                // Optionally, show a success message
                // alert('Person deleted successfully!');
            },
            error: function(xhr, status, error) {
                // Optionally, show an error message
                alert('An error occurred while deleting the person: ' + error);
            }
        });
    }
}