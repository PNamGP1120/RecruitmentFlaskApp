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

function verifiedApply(applyId, action) {
    const form = document.getElementById(`verify-apply-form-${applyId}`);
    const formData = new FormData(form);
    const messagebox = document.getElementById(`message-verified-apply-${applyId}`);

    formData.set("med", action); // set thủ công thay vì rely vào hidden input

    fetch(`/api/verified-apply/${applyId}`, {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        console.log("Dữ liệu trả về:", data.message);
        messagebox.innerText = data.message;

        alert(data.message);

        const modal = document.getElementById(`modal${applyId}`);
         const modalInstance = bootstrap.Modal.getInstance(modal);
        if (modalInstance) {
            modalInstance.hide();
        }

        const spanStatus = document.getElementById(`status-${applyId}`);
        let text = "";
        let classList = ["badge", "mb-2", "p-2"];

        switch (action) {
            case "Confirm":
                text = "Status: Confirmed";
                classList.push("bg-info", "text-dark");
                break;
            case "Reject":
                text = "Status: Rejected";
                classList.push("bg-danger");
                break;
            case "Accept":
                text = "Status: Accepted";
                classList.push("bg-success");
                break;
            default:
                text = "Status: Unknown";
                classList.push("bg-secondary");
                break;
        }

        spanStatus.className = classList.join(" ");
        spanStatus.innerText = text;
    })
    .catch(err => {
        console.error("Lỗi khi xác nhận:", err);
        messagebox.innerText = "Đã xảy ra lỗi khi xác nhận.";
    });
}




