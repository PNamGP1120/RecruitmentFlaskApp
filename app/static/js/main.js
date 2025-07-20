document.addEventListener("DOMContentLoaded", function() {
    const urlParams = new URLSearchParams(window.location.search);
    const currentPage = urlParams.get('page') || '1';
    let item = document.getElementById(`page${currentPage}`);
    console.info(item);
    item.classList.add('active');
  });

document.addEventListener('DOMContentLoaded', function() {
        document.querySelectorAll('.update-cv-btn').forEach(button => {
            button.addEventListener('click', function() {
                const cvId = this.dataset.cvId;
                const updateForm = document.getElementById(`update-form-${cvId}`);
                if (updateForm) {
                    updateForm.style.display = 'table-row'; // Show the form
                }
            });
        });

        document.querySelectorAll('.cancel-update-btn').forEach(button => {
            button.addEventListener('click', function() {
                const cvId = this.dataset.cvId;
                const updateForm = document.getElementById(`update-form-${cvId}`);
                if (updateForm) {
                    updateForm.style.display = 'none'; // Hide the form
                }
            });
        });
    });