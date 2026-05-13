function setupLoginForm() {
  const form = document.getElementById("loginForm");
  if (!form) return;

  const usernameEmail = form.elements["usernameEmail"];
  const password = form.elements["password"];
  const usernameEmailFeedback = document.getElementById("usernameEmailFeedback");
  const passwordFeedback = document.getElementById("passwordFeedback");

  function showFeedback(input, feedback) {
    if (!input.value) {
      feedback.textContent = "Please fill in this field";
      feedback.style.color = "red";
    } else {
      feedback.textContent = "";
    }
  }

  usernameEmail.addEventListener("blur", () => showFeedback(usernameEmail, usernameEmailFeedback));
  password.addEventListener("blur", () => showFeedback(password, passwordFeedback));

  form.addEventListener("submit", function (e) {
    showFeedback(usernameEmail, usernameEmailFeedback);
    showFeedback(password, passwordFeedback);
    if (!usernameEmail.value || !password.value) e.preventDefault();
  });
}
setupLoginForm();
