const API_BASE_URL = "http://127.0.0.1:8000";
const TOKEN_STORAGE_KEY = "recallai_access_token";

const authView = document.querySelector("#auth-view");
const dashboardView = document.querySelector("#dashboard-view");
const registerForm = document.querySelector("#register-form");
const loginForm = document.querySelector("#login-form");
const registerButton = document.querySelector("#register-button");
const loginButton = document.querySelector("#login-button");
const registerStatus = document.querySelector("#register-status");
const loginStatus = document.querySelector("#login-status");
const authenticatedUsername = document.querySelector("#authenticated-username");
const authenticatedEmail = document.querySelector("#authenticated-email");
const logoutButton = document.querySelector("#logout-button");
const dashboardStatus = document.querySelector("#dashboard-status");
const generateForm = document.querySelector("#generate-form");
const generateButton = document.querySelector("#generate-button");
const generationStatus = document.querySelector("#generation-status");
const studyResults = document.querySelector("#study-results");
const resultTopic = document.querySelector("#result-topic");
const summaryContent = document.querySelector("#summary-content");
const keyConceptsList = document.querySelector("#key-concepts-list");
const flashcardsList = document.querySelector("#flashcards-list");
const quizQuestionsList = document.querySelector("#quiz-questions-list");
const createStudyView = document.querySelector("#create-study-view");
const savedGuidesView = document.querySelector("#saved-guides-view");
const showCreateButton = document.querySelector("#show-create-button");
const showSavedButton = document.querySelector("#show-saved-button");
const saveGuideButton = document.querySelector("#save-guide-button");
const saveStatus = document.querySelector("#save-status");
const refreshSavedButton = document.querySelector("#refresh-saved-button");
const savedGuidesStatus = document.querySelector("#saved-guides-status");
const savedGuidesList = document.querySelector("#saved-guides-list");

let currentStudyMaterial = null;

function setStatus(element, message, type = "") {
  element.className = `form-status ${type}`.trim();
  element.textContent = message;
}

function getErrorMessage(data, fallbackMessage) {
  if (typeof data?.detail === "string") {
    return data.detail;
  }

  if (Array.isArray(data?.detail) && data.detail.length > 0) {
    return data.detail[0].msg;
  }

  return fallbackMessage;
}

async function sendApiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const error = new Error(
      getErrorMessage(data, `Request failed with status ${response.status}.`)
    );
    error.status = response.status;
    throw error;
  }

  return data;
}

function showAuthenticatedDashboard(user) {
  authenticatedUsername.textContent = user.username;
  authenticatedEmail.textContent = user.email;
  authView.hidden = true;
  dashboardView.hidden = false;
  showCreateStudyView();
  setStatus(dashboardStatus, "");
}

function showAuthenticationForms(message = "") {
  dashboardView.hidden = true;
  authView.hidden = false;
  authenticatedUsername.textContent = "";
  authenticatedEmail.textContent = "";
  studyResults.hidden = true;
  savedGuidesList.replaceChildren();
  generateForm.reset();
  currentStudyMaterial = null;
  setStatus(generationStatus, "");
  setStatus(saveStatus, "");
  setStatus(savedGuidesStatus, "");
  setStatus(loginStatus, message, message ? "success" : "");
}

function showCreateStudyView() {
  createStudyView.hidden = false;
  savedGuidesView.hidden = true;
  showCreateButton.classList.add("active");
  showSavedButton.classList.remove("active");
}

function showSavedGuidesView() {
  createStudyView.hidden = true;
  savedGuidesView.hidden = false;
  showCreateButton.classList.remove("active");
  showSavedButton.classList.add("active");
}

function createTextElement(tagName, className, text) {
  const element = document.createElement(tagName);
  element.className = className;
  element.textContent = text;
  return element;
}

function renderStudyMaterial(material, { canSave = false } = {}) {
  resultTopic.textContent = material.topic;
  summaryContent.textContent = material.summary;
  keyConceptsList.replaceChildren();
  flashcardsList.replaceChildren();
  quizQuestionsList.replaceChildren();
  currentStudyMaterial = canSave ? material : null;
  saveGuideButton.hidden = !canSave;
  saveGuideButton.disabled = false;
  saveGuideButton.textContent = "Save study guide";
  setStatus(saveStatus, "");

  material.key_concepts.forEach((concept) => {
    const conceptItem = document.createElement("article");
    conceptItem.className = "concept-item";
    conceptItem.append(
      createTextElement("h4", "", concept.name),
      createTextElement("p", "", concept.explanation)
    );
    keyConceptsList.append(conceptItem);
  });

  material.flashcards.forEach((flashcard, index) => {
    const card = document.createElement("article");
    card.className = "flashcard";
    card.append(
      createTextElement("span", "item-number", `Card ${index + 1}`),
      createTextElement("h4", "", flashcard.question),
      createTextElement("p", "flashcard-answer", flashcard.answer)
    );
    flashcardsList.append(card);
  });

  material.quiz_questions.forEach((quizQuestion, index) => {
    const item = document.createElement("article");
    item.className = "quiz-item";

    const heading = document.createElement("div");
    heading.className = "quiz-heading";
    heading.append(
      createTextElement("span", "item-number", `Question ${index + 1}`),
      createTextElement(
        "span",
        `difficulty difficulty-${quizQuestion.difficulty}`,
        quizQuestion.difficulty
      )
    );

    const answer = document.createElement("details");
    answer.append(
      createTextElement("summary", "", "Show answer"),
      createTextElement("p", "", quizQuestion.answer)
    );

    item.append(heading, createTextElement("h4", "", quizQuestion.question), answer);
    quizQuestionsList.append(item);
  });

  studyResults.hidden = false;
  studyResults.scrollIntoView({ behavior: "smooth", block: "start" });
}

function handleAuthenticationFailure(error) {
  if (error.status !== 401) {
    return false;
  }

  localStorage.removeItem(TOKEN_STORAGE_KEY);
  showAuthenticationForms("Your session expired. Please sign in again.");
  return true;
}

function renderSavedGuideList(guides) {
  savedGuidesList.replaceChildren();

  if (guides.length === 0) {
    const emptyState = document.createElement("div");
    emptyState.className = "empty-state";
    emptyState.append(
      createTextElement("h3", "", "No saved study guides yet"),
      createTextElement(
        "p",
        "",
        "Generate a study guide, then use Save study guide to add it here."
      )
    );
    savedGuidesList.append(emptyState);
    return;
  }

  guides.forEach((guide) => {
    const card = document.createElement("article");
    card.className = "saved-guide-card";

    const details = document.createElement("div");
    details.append(
      createTextElement("h3", "", guide.title),
      createTextElement(
        "p",
        "saved-date",
        `Saved ${new Date(guide.created_at).toLocaleString()}`
      )
    );

    const openButton = createTextElement("button", "secondary-button", "Open guide");
    openButton.type = "button";
    openButton.addEventListener("click", () => openSavedGuide(guide.id));

    card.append(details, openButton);
    savedGuidesList.append(card);
  });
}

async function loadSavedGuides() {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY);
  if (!token) {
    showAuthenticationForms("Please sign in to view saved study guides.");
    return;
  }

  refreshSavedButton.disabled = true;
  setStatus(savedGuidesStatus, "Loading your saved study guides...");

  try {
    const guides = await sendApiRequest("/topics", {
      headers: { Authorization: `Bearer ${token}` },
    });
    renderSavedGuideList(guides);
    setStatus(
      savedGuidesStatus,
      guides.length === 0 ? "" : `${guides.length} saved study guide${guides.length === 1 ? "" : "s"}.`,
      guides.length === 0 ? "" : "success"
    );
  } catch (error) {
    if (!handleAuthenticationFailure(error)) {
      setStatus(savedGuidesStatus, error.message, "error");
    }
  } finally {
    refreshSavedButton.disabled = false;
  }
}

async function openSavedGuide(topicId) {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY);
  setStatus(savedGuidesStatus, "Opening saved study guide...");

  try {
    const material = await sendApiRequest(`/topics/${topicId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    showCreateStudyView();
    renderStudyMaterial(material);
    setStatus(generationStatus, "Loaded from your saved study guides.", "success");
  } catch (error) {
    if (!handleAuthenticationFailure(error)) {
      setStatus(savedGuidesStatus, error.message, "error");
    }
  }
}

async function loadCurrentUser(token) {
  return sendApiRequest("/auth/me", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

registerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  registerButton.disabled = true;
  setStatus(registerStatus, "Creating your account...");

  const registration = {
    username: document.querySelector("#register-username").value,
    email: document.querySelector("#register-email").value,
    password: document.querySelector("#register-password").value,
  };

  try {
    const user = await sendApiRequest("/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(registration),
    });

    registerForm.reset();
    document.querySelector("#login-identifier").value = user.username;
    setStatus(registerStatus, "Account created. You can now sign in.", "success");
    document.querySelector("#login-password").focus();
  } catch (error) {
    setStatus(registerStatus, error.message, "error");
  } finally {
    registerButton.disabled = false;
  }
});

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  loginButton.disabled = true;
  setStatus(loginStatus, "Signing in...");

  const loginData = {
    identifier: document.querySelector("#login-identifier").value,
    password: document.querySelector("#login-password").value,
  };

  try {
    const tokenData = await sendApiRequest("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(loginData),
    });

    localStorage.setItem(TOKEN_STORAGE_KEY, tokenData.access_token);
    const user = await loadCurrentUser(tokenData.access_token);
    loginForm.reset();
    showAuthenticatedDashboard(user);
  } catch (error) {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    setStatus(loginStatus, error.message, "error");
  } finally {
    loginButton.disabled = false;
  }
});

logoutButton.addEventListener("click", () => {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
  showAuthenticationForms("You have been logged out.");
});

showCreateButton.addEventListener("click", showCreateStudyView);

showSavedButton.addEventListener("click", () => {
  showSavedGuidesView();
  loadSavedGuides();
});

refreshSavedButton.addEventListener("click", loadSavedGuides);

saveGuideButton.addEventListener("click", async () => {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY);
  if (!token || !currentStudyMaterial) {
    setStatus(saveStatus, "Generate a study guide before saving.", "error");
    return;
  }

  saveGuideButton.disabled = true;
  saveGuideButton.textContent = "Saving...";
  setStatus(saveStatus, "Saving this study guide...");

  try {
    await sendApiRequest("/topics", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(currentStudyMaterial),
    });
    saveGuideButton.textContent = "Saved";
    setStatus(saveStatus, "Study guide saved successfully.", "success");
  } catch (error) {
    if (!handleAuthenticationFailure(error)) {
      saveGuideButton.disabled = false;
      saveGuideButton.textContent = "Save study guide";
      setStatus(saveStatus, error.message, "error");
    }
  }
});

generateForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const token = localStorage.getItem(TOKEN_STORAGE_KEY);

  if (!token) {
    showAuthenticationForms("Please sign in before generating study material.");
    return;
  }

  generateButton.disabled = true;
  generateButton.textContent = "Generating...";
  studyResults.hidden = true;
  currentStudyMaterial = null;
  setStatus(generationStatus, "Gemini is building your study guide...");

  try {
    const material = await sendApiRequest("/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        topic: document.querySelector("#topic-input").value.trim(),
      }),
    });

    renderStudyMaterial(material, { canSave: true });
    setStatus(generationStatus, "Study guide generated successfully.", "success");
  } catch (error) {
    if (!handleAuthenticationFailure(error)) {
      setStatus(generationStatus, error.message, "error");
    }
  } finally {
    generateButton.disabled = false;
    generateButton.textContent = "Generate study guide";
  }
});

async function restoreAuthenticatedSession() {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY);
  if (!token) {
    return;
  }

  try {
    const user = await loadCurrentUser(token);
    showAuthenticatedDashboard(user);
  } catch {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    showAuthenticationForms("Your session expired. Please sign in again.");
  }
}

restoreAuthenticatedSession();
