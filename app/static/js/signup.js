function initSignupStepper() {
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
    setStep(2);
  });

  toStepOneBtn.addEventListener("click", function () {
    setStep(1);
  });

  setStep(1);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initSignupStepper);
} else {
  initSignupStepper();
}
