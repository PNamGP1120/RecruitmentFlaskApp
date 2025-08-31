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

            case "Reject":
                text = "Status: Rejected";

            case "Accept":
                text = "Status: Accepted";

            default:
               location.reload();
        }

        spanStatus.className = classList.join(" ");
        spanStatus.innerText = text;
    })
    .catch(err => {
        console.error("Lỗi khi xác nhận:", err);
        messagebox.innerText = "Đã xảy ra lỗi khi xác nhận.";
    });
}


async function verifiedRecruiter(userId) {
    fetch(`/api/verified-recruiter/${userId}`,{
    method: "POST"
    }).then(res => res.json()).then(data => {
    if (data.status === 200){
        alert("verified successful");
        location.reload();
    }
    else{
        alert("Verified successful");
        location.reload();
    }
    })
}

async function cancelRecruiter(userId) {
    if(confirm("Are you sure you want to cancel this employer's permission?") == true){
    fetch(`/api/cancel-recruiter/${userId}`,{
    method: "POST"
    }).then(res => res.json()).then(data => {
    if (data.status === 200){
        alert("Cancel successful");
        location.reload();
    }
    else{
        alert("Cancel Failed");
        location.reload();
    }
    })
    }
}


async function createDatetimeInterview(applyId) {
    const value = document.getElementById(`datetime_interview_${applyId}`).value;
    console.log("value datetime", value);
    let formDataDatetime = new FormData();
    formDataDatetime.append("date", value);

    if (!value){
        alert("Vui lòng chọn ngày giờ!");

    }
    else {
    if(confirm(`Bạn chắc chắn muốn tạo lịch vào ${value}`) === true){
    // Hiện loading
        const btn = document.getElementById(`button_create_${applyId}`);
        const loading = document.getElementById(`loading_${applyId}`);
        btn.disabled = true;
        loading.style.display = "inline";

        try {
            const res = await fetch(`/api/${applyId}/create_link`, {
                method: "POST",
                body: formDataDatetime
            });
            const data = await res.json();

            if (data.status === 201) {
                alert("Tạo lịch thành công!");
            } else {
                alert("Tạo lịch thất bại!");
            }
            location.reload();
        } catch (err) {
            alert(`Xảy ra lỗi: ${err}`);
            location.reload();
        } finally {
            // Ẩn loading, bật lại nút
            btn.disabled = false;
            loading.style.display = "none";
        }
    }
    }

}


    const salaryRange = document.getElementById("salaryRange");
    const salaryText = document.getElementById("salaryText");

    const formatter = new Intl.NumberFormat("vi-VN", {
        style: "currency",
        currency: "VND",
        minimumFractionDigits: 0
    });

    salaryRange.addEventListener("input", function () {
    const formatter = new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        minimumFractionDigits: 0
    });
    console.log("salary", salaryRange.value)
    salaryText.textContent = `Salary: ${formatter.format(salaryRange.value)} - ${formatter.format(salaryRange.max)}`;
});


