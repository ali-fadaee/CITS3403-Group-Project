// Utility Functions
// Checks if password meets the requirements
function checkPassword(value) {
  const hasLower = /[a-z]/.test(value);
  const hasUpper = /[A-Z]/.test(value);
  const hasDigit = /\d/.test(value);
  const lengthCheck = value.length >= 8;
  return lengthCheck && hasLower && hasUpper && hasDigit;
}

// Checks if username meets the requirements
function checkUsername(value) {
  return (
    value.length >= 3 && value.length <= 20 && /^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]$/.test(value)
  );
}

// Generic function to update feedback based on input validity
// sets a timeout to avoid excessive updates/feedbacks while typing - better for user experience
function createFeedbackUpdate(input, feedback, isValid, messages, delay = true) {
  let timeout;
  return function () {
    clearTimeout(timeout);
    const update = () => {
      if (!feedback) return;
      if (!input.value) {
        feedback.textContent = "Please fill in this field";
        feedback.style.color = "red";
        return;
      }
      const valid = isValid();
      feedback.textContent = valid ? messages.valid : messages.invalid;
      feedback.style.color = valid ? "green" : "red";
    };
    if (delay) {
      timeout = setTimeout(update, 1000); // Delay of 1s after user stops typing
    } else {
      update(); // Immediate update for events using blur
    }
  };
}

// Client side validation checks for the signup form, 
// Provides quick feedback to the user as they fill out the form
function signupValidation(form) {
  const email = form.elements["email"];
  const password = form.elements["password"];
  const confirmPassword = form.elements["confirm_password"];
  const username = form.elements["username"];
  const emailFeedback = document.getElementById("emailFeedback");
  const passwordFeedback = document.getElementById("passwordFeedback");
  const confirmPasswordFeedback = document.getElementById("confirmPasswordFeedback");
  const usernameFeedback = document.getElementById("usernameFeedback");

  if (!email || !password || !confirmPassword) return;
  
  const updateEmailFeedback = createFeedbackUpdate(email, emailFeedback, () => email.checkValidity(), {
    valid: "Email looks good!",
    invalid: "Please enter a valid email address."
  } ,false);

  const updatePasswordFeedback = createFeedbackUpdate(password, passwordFeedback, () => checkPassword(password.value), {
    valid: "Password looks good!",
    invalid: "Password does not meet requirements."
  });

  const updateConfirmFeedback = createFeedbackUpdate(confirmPassword, confirmPasswordFeedback, () => confirmPassword.value === password.value, {
    valid: "Passwords match!",
    invalid: "Passwords do not match."
  });

  const updateUsernameFeedback = createFeedbackUpdate(username, usernameFeedback, () => checkUsername(username.value), {
    valid: "Username looks good!",
    invalid: "Username does not meet requirements."
  });

  // Attach event listeners for real-time feedback 
  email.addEventListener("blur", updateEmailFeedback);
  password.addEventListener("input", function () {
    updatePasswordFeedback();
    if (confirmPassword.value) updateConfirmFeedback();});  // only update if confirm field has content

  confirmPassword.addEventListener("input", updateConfirmFeedback);
  username.addEventListener("input", updateUsernameFeedback);

  // Used for the Signup "Continue" button on the first step to validate before proceeding 
  function continue_check() {
    return (email.checkValidity() && checkPassword(password.value) && confirmPassword.value === password.value);
  }

  // Final check on form submission to prevent submission if username is invalid
  form.addEventListener("submit", function(e) {
  if (!checkUsername(username.value)) e.preventDefault();});

  return {continue_check};
}

// Handles the multi-step form navigation for the signup process
function initSignupStepper(form, validated) {
  const panels = document.getElementById("signupPanels");
  const toStepTwoBtn = document.getElementById("continueToProfile");
  const toStepOneBtn = document.getElementById("backToVerify");
  const progressBar = document.getElementById("signupProgress");
  const progressText = document.getElementById("signupProgressText");

  if (!panels || !toStepTwoBtn || !toStepOneBtn) {
    return;
  }

  function setStep(step) {
    const isStepOne = step === 1;
    panels.classList.toggle("is-step-two", !isStepOne);
    if (progressBar) {
      progressBar.classList.toggle("is-step-two", !isStepOne);
      progressBar.setAttribute("aria-valuenow", String(step));
    }
    if (progressText) {
      progressText.textContent = isStepOne
        ? "Step 1 of 2 - Account details"
        : "Step 2 of 2 - Profile setup";
    }
  }

  toStepTwoBtn.addEventListener("click", function () {
    if (validated()) {
      setStep(2);
    } 
    else{
      form.reportValidity(); //triggers browser's validation UI when no input provided
    }
  });

  toStepOneBtn.addEventListener("click", function () {
    setStep(1);
  });
  const startStep = panels.getAttribute("data-start-step");
  if (startStep === "2") setStep(2);
  else setStep(1);
}

// Counts the number of selected interests and updates the display
function interestCounter(form) {
  const interests = form ? form.elements["interests[]"] : null;
  const count = document.getElementById("interestCount");

  if (!interests || !count) {
    return;
  }

  function updateCount() {
    let selected = 0;
    for (let i = 0; i < interests.length; i++) {
      if (interests[i].checked) {
        selected++;
      }
    }
    count.textContent = String(selected);
  }

  for (let i = 0; i < interests.length; i++) {
    interests[i].addEventListener("change", updateCount);
  }
  updateCount();
}

// Initializes the client side signup form functionality
// Sets up client side client_validation, multi-step navigation, and interest counting
function setupSignupForm() {
  const form = document.getElementById("signupForm");
  if (!form) return;
  const client_validation = signupValidation(form);

  if (!client_validation) return;
  initSignupStepper(form, client_validation.continue_check);
  interestCounter(form);
}
setupSignupForm();  