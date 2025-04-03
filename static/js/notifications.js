// Function to show notification toast
function showNotification(title, message, type = "success") {
    const toast = document.getElementById("notificationToast");
    if (!toast) return;

    const toastTitle = document.getElementById("toastTitle");
    const toastMessage = document.getElementById("toastMessage");

    toastTitle.innerText = title;
    toastMessage.innerText = message;

    // Set toast color based on type
    toast.className = "toast";
    if (type === "success") {
        toast.classList.add("bg-success", "text-white");
    } else if (type === "error") {
        toast.classList.add("bg-danger", "text-white");
    } else if (type === "warning") {
        toast.classList.add("bg-warning");
    } else if (type === "info") {
        toast.classList.add("bg-info", "text-white");
    }

    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

// Make function globally accessible
window.showNotification = showNotification; 