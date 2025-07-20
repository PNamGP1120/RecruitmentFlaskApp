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

async function apply(jobId) {
    const form = document.getElementById("applyForm");
    const formData = new FormData(form);
    const message = document.getElementById("error-apply");

    try {
        const response = await fetch(`/api/apply/${jobId}`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();


        if (response.status !== 200) {
            // Giả sử server trả về: {"error": "You have already applied"}
            message.innerText = data.message || "Đã xảy ra lỗi khi nộp đơn.";
        } else {
            alert(data.message || "You have successfully applied.");
            window.location.href = "/applications";  // hoặc location.reload()
        }
    } catch (err) {
        console.error("Lỗi khi gửi form:", err);
        message.innerText = "Không thể kết nối đến server.";
    }
}


