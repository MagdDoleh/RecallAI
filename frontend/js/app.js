const LOCAL_FRONTEND_HOSTS = new Set(["127.0.0.1", "localhost"]);
const IS_LOCAL_STATIC_SERVER =
  LOCAL_FRONTEND_HOSTS.has(window.location.hostname) && window.location.port === "5500";
const API_BASE_URL = IS_LOCAL_STATIC_SERVER
  ? "http://127.0.0.1:8000"
  : window.location.origin;
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
const savedGuideControls = document.querySelector("#saved-guide-controls");
const editGuideButton = document.querySelector("#edit-guide-button");
const deleteOpenGuideButton = document.querySelector("#delete-open-guide-button");
const editGuideForm = document.querySelector("#edit-guide-form");
const editTopicInput = document.querySelector("#edit-topic-input");
const editSummaryInput = document.querySelector("#edit-summary-input");
const editKeyConceptsFields = document.querySelector("#edit-key-concepts-fields");
const editFlashcardsFields = document.querySelector("#edit-flashcards-fields");
const editQuizFields = document.querySelector("#edit-quiz-fields");
const updateGuideButton = document.querySelector("#update-guide-button");
const cancelEditButton = document.querySelector("#cancel-edit-button");
const editGuideStatus = document.querySelector("#edit-guide-status");
const savedSearchForm = document.querySelector("#saved-search-form");
const savedSearchInput = document.querySelector("#saved-search-input");
const clearSearchButton = document.querySelector("#clear-search-button");
const dashboardHomeView = document.querySelector("#dashboard-home-view");
const accountView = document.querySelector("#account-view");
const showDashboardButton = document.querySelector("#show-dashboard-button");
const showAccountButton = document.querySelector("#show-account-button");
const dashboardCreateButton = document.querySelector("#dashboard-create-button");
const viewAllSavedButton = document.querySelector("#view-all-saved-button");
const welcomeUsername = document.querySelector("#welcome-username");
const savedGuideCount = document.querySelector("#saved-guide-count");
const recentGuidesList = document.querySelector("#recent-guides-list");
const dashboardLibraryStatus = document.querySelector("#dashboard-library-status");
const accountUsername = document.querySelector("#account-username");
const accountEmail = document.querySelector("#account-email");
const accountDetailUsername = document.querySelector("#account-detail-username");
const accountDetailEmail = document.querySelector("#account-detail-email");
const accountCreatedAt = document.querySelector("#account-created-at");
const accountSavedCount = document.querySelector("#account-saved-count");
const accountLogoutButton = document.querySelector("#account-logout-button");
const sidebarUserAvatar = document.querySelector("#sidebar-user-avatar");
const accountAvatar = document.querySelector("#account-avatar");
const appSidebar = document.querySelector("#app-sidebar");
const mobileMenuButton = document.querySelector("#mobile-menu-button");
const sidebarOverlay = document.querySelector("#sidebar-overlay");

let currentStudyMaterial = null;
let currentSavedGuide = null;
let savedGuidesRequestNumber = 0;
let currentUser = null;
let savedGuidesCache = [];

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
  currentUser = user;
  authenticatedUsername.textContent = user.username;
  authenticatedEmail.textContent = user.email;
  welcomeUsername.textContent = user.username;
  accountUsername.textContent = user.username;
  accountEmail.textContent = user.email;
  accountDetailUsername.textContent = user.username;
  accountDetailEmail.textContent = user.email;
  accountCreatedAt.textContent = new Date(user.created_at).toLocaleDateString(undefined, {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
  const initial = user.username.charAt(0).toUpperCase();
  sidebarUserAvatar.textContent = initial;
  accountAvatar.textContent = initial;
  authView.hidden = true;
  dashboardView.hidden = false;
  showDashboardHomeView();
  loadDashboardLibrary();
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
  editGuideForm.reset();
  editGuideForm.hidden = true;
  currentStudyMaterial = null;
  currentSavedGuide = null;
  currentUser = null;
  savedGuidesCache = [];
  closeMobileNavigation();
  setStatus(generationStatus, "");
  setStatus(saveStatus, "");
  setStatus(savedGuidesStatus, "");
  setStatus(editGuideStatus, "");
  setStatus(loginStatus, message, message ? "success" : "");
}

function setActiveView(viewName) {
  dashboardHomeView.hidden = viewName !== "dashboard";
  createStudyView.hidden = viewName !== "create";
  savedGuidesView.hidden = viewName !== "saved";
  accountView.hidden = viewName !== "account";

  for (const button of [
    showDashboardButton,
    showCreateButton,
    showSavedButton,
    showAccountButton,
  ]) {
    const isActive = button.dataset.view === viewName;
    button.classList.toggle("active", isActive);
    if (isActive) button.setAttribute("aria-current", "page");
    else button.removeAttribute("aria-current");
  }
  closeMobileNavigation();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function showDashboardHomeView() {
  setActiveView("dashboard");
}

function showCreateStudyView() {
  setActiveView("create");
}

function showSavedGuidesView() {
  setActiveView("saved");
}

function showAccountView() {
  setActiveView("account");
  accountSavedCount.textContent = savedGuidesCache.length;
}

function openMobileNavigation() {
  appSidebar.classList.add("open");
  sidebarOverlay.hidden = false;
  mobileMenuButton.setAttribute("aria-expanded", "true");
}

function closeMobileNavigation() {
  appSidebar.classList.remove("open");
  sidebarOverlay.hidden = true;
  mobileMenuButton.setAttribute("aria-expanded", "false");
}

function createTextElement(tagName, className, text) {
  const element = document.createElement(tagName);
  element.className = className;
  element.textContent = text;
  return element;
}

function formatGuideDate(dateValue) {
  return new Date(dateValue).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function renderRecentGuides(guides) {
  recentGuidesList.replaceChildren();
  if (guides.length === 0) {
    const emptyState = document.createElement("div");
    emptyState.className = "empty-state";
    emptyState.append(
      createTextElement("h3", "", "No study guides yet"),
      createTextElement(
        "p",
        "",
        "Create your first AI study guide to start building your library."
      )
    );
    const createButton = createTextElement("button", "button button-primary", "Create your first guide");
    createButton.type = "button";
    createButton.addEventListener("click", showCreateStudyView);
    emptyState.append(createButton);
    recentGuidesList.append(emptyState);
    return;
  }

  guides.slice(0, 3).forEach((guide) => {
    const card = document.createElement("article");
    card.className = "recent-guide-card";
    card.append(
      createTextElement("div", "guide-card-icon", "▤"),
      createTextElement("h3", "", guide.title),
      createTextElement("p", "saved-date", `Updated ${formatGuideDate(guide.updated_at)}`)
    );
    const openButton = createTextElement("button", "text-action", "Open guide →");
    openButton.type = "button";
    openButton.addEventListener("click", () => openSavedGuide(guide.id));
    card.append(openButton);
    recentGuidesList.append(card);
  });
}

async function loadDashboardLibrary() {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY);
  if (!token) return;
  setStatus(dashboardLibraryStatus, "Loading your library...");
  try {
    const guides = await sendApiRequest("/topics", {
      headers: { Authorization: `Bearer ${token}` },
    });
    savedGuidesCache = guides;
    savedGuideCount.textContent = guides.length;
    accountSavedCount.textContent = guides.length;
    renderRecentGuides(guides);
    setStatus(dashboardLibraryStatus, "");
  } catch (error) {
    if (!handleAuthenticationFailure(error)) {
      savedGuideCount.textContent = "—";
      setStatus(dashboardLibraryStatus, error.message, "error");
    }
  }
}

function renderStudyMaterial(material, { canSave = false, isSaved = false } = {}) {
  resultTopic.textContent = material.topic;
  summaryContent.textContent = material.summary;
  keyConceptsList.replaceChildren();
  flashcardsList.replaceChildren();
  quizQuestionsList.replaceChildren();
  currentStudyMaterial = canSave ? material : null;
  currentSavedGuide = isSaved ? material : null;
  saveGuideButton.hidden = !canSave;
  savedGuideControls.hidden = !isSaved;
  editGuideForm.hidden = true;
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
    card.tabIndex = 0;
    card.setAttribute("role", "button");
    card.setAttribute("aria-expanded", "false");
    card.append(
      createTextElement("span", "item-number", `Card ${index + 1}`),
      createTextElement("h4", "", flashcard.question),
      createTextElement("p", "flashcard-answer", flashcard.answer)
    );
    const toggleCard = () => {
      const revealed = card.classList.toggle("revealed");
      card.setAttribute("aria-expanded", String(revealed));
    };
    card.addEventListener("click", toggleCard);
    card.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        toggleCard();
      }
    });
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

function renderSavedGuideList(guides, searchTerm = "") {
  savedGuidesList.replaceChildren();

  if (guides.length === 0) {
    const emptyState = document.createElement("div");
    emptyState.className = "empty-state";
    emptyState.append(
      createTextElement(
        "h3",
        "",
        searchTerm ? "No matching study guides" : "No saved study guides yet"
      ),
      createTextElement(
        "p",
        "",
        searchTerm
          ? `No saved titles contain “${searchTerm}”.`
          : "Generate a study guide, then use Save study guide to add it here."
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
        `Updated ${formatGuideDate(guide.updated_at)}`
      )
    );

    const actions = document.createElement("div");
    actions.className = "saved-guide-actions";

    const openButton = createTextElement("button", "secondary-button", "Open");
    openButton.type = "button";
    openButton.addEventListener("click", () => openSavedGuide(guide.id));

    const editButton = createTextElement("button", "secondary-button", "Edit");
    editButton.type = "button";
    editButton.addEventListener("click", () => openSavedGuide(guide.id, { startEditing: true }));

    const deleteButton = createTextElement("button", "danger-button", "Delete");
    deleteButton.type = "button";
    deleteButton.addEventListener("click", () => deleteSavedGuide(guide.id, guide.title));

    actions.append(openButton, editButton, deleteButton);
    card.append(details, actions);
    savedGuidesList.append(card);
  });
}

async function loadSavedGuides() {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY);
  if (!token) {
    showAuthenticationForms("Please sign in to view saved study guides.");
    return;
  }

  const requestNumber = ++savedGuidesRequestNumber;
  refreshSavedButton.disabled = true;
  setStatus(savedGuidesStatus, "Loading your saved study guides...");

  try {
    const searchTerm = savedSearchInput.value.trim();
    const query = searchTerm ? `?search=${encodeURIComponent(searchTerm)}` : "";
    const guides = await sendApiRequest(`/topics${query}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (requestNumber !== savedGuidesRequestNumber) {
      return;
    }
    if (!searchTerm) {
      savedGuidesCache = guides;
      savedGuideCount.textContent = guides.length;
      accountSavedCount.textContent = guides.length;
      renderRecentGuides(guides);
    }
    renderSavedGuideList(guides, searchTerm);
    setStatus(
      savedGuidesStatus,
      guides.length === 0 ? "" : `${guides.length} saved study guide${guides.length === 1 ? "" : "s"}.`,
      guides.length === 0 ? "" : "success"
    );
  } catch (error) {
    if (requestNumber !== savedGuidesRequestNumber) {
      return;
    }
    if (!handleAuthenticationFailure(error)) {
      setStatus(savedGuidesStatus, error.message, "error");
    }
  } finally {
    if (requestNumber === savedGuidesRequestNumber) {
      refreshSavedButton.disabled = false;
    }
  }
}

async function openSavedGuide(topicId, { startEditing = false } = {}) {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY);
  setStatus(savedGuidesStatus, "Opening saved study guide...");

  try {
    const material = await sendApiRequest(`/topics/${topicId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    showCreateStudyView();
    renderStudyMaterial(material, { isSaved: true });
    setStatus(generationStatus, "Loaded from your saved study guides.", "success");
    if (startEditing) {
      beginEditingCurrentGuide();
    }
  } catch (error) {
    if (!handleAuthenticationFailure(error)) {
      setStatus(savedGuidesStatus, error.message, "error");
    }
  }
}

function addEditField(container, labelText, value, className, maxLength) {
  const fieldWrapper = document.createElement("div");
  fieldWrapper.className = "edit-field";

  const label = document.createElement("label");
  label.textContent = labelText;

  const field = document.createElement("textarea");
  field.className = className;
  field.value = value;
  field.rows = 3;
  field.maxLength = maxLength;
  field.required = true;

  fieldWrapper.append(label, field);
  container.append(fieldWrapper);
}

function addDifficultyField(container, difficulty) {
  const fieldWrapper = document.createElement("div");
  fieldWrapper.className = "edit-field";

  const label = document.createElement("label");
  label.textContent = "Difficulty";

  const select = document.createElement("select");
  select.className = "edit-quiz-difficulty";
  for (const level of ["easy", "medium", "hard"]) {
    const option = document.createElement("option");
    option.value = level;
    option.textContent = level;
    option.selected = level === difficulty;
    select.append(option);
  }

  fieldWrapper.append(label, select);
  container.append(fieldWrapper);
}

function beginEditingCurrentGuide() {
  if (!currentSavedGuide) {
    return;
  }

  editTopicInput.value = currentSavedGuide.topic;
  editSummaryInput.value = currentSavedGuide.summary;
  editKeyConceptsFields.replaceChildren();
  editFlashcardsFields.replaceChildren();
  editQuizFields.replaceChildren();

  currentSavedGuide.key_concepts.forEach((concept, index) => {
    const row = document.createElement("article");
    row.className = "edit-row edit-concept-row";
    row.append(createTextElement("h3", "", `Concept ${index + 1}`));
    addEditField(row, "Name", concept.name, "edit-concept-name", 120);
    addEditField(
      row,
      "Explanation",
      concept.explanation,
      "edit-concept-explanation",
      1000
    );
    editKeyConceptsFields.append(row);
  });

  currentSavedGuide.flashcards.forEach((flashcard, index) => {
    const row = document.createElement("article");
    row.className = "edit-row edit-flashcard-row";
    row.append(createTextElement("h3", "", `Flashcard ${index + 1}`));
    addEditField(row, "Question", flashcard.question, "edit-flashcard-question", 500);
    addEditField(row, "Answer", flashcard.answer, "edit-flashcard-answer", 1000);
    editFlashcardsFields.append(row);
  });

  currentSavedGuide.quiz_questions.forEach((question, index) => {
    const row = document.createElement("article");
    row.className = "edit-row edit-quiz-row";
    row.append(createTextElement("h3", "", `Quiz question ${index + 1}`));
    addEditField(row, "Question", question.question, "edit-quiz-question", 500);
    addEditField(row, "Answer", question.answer, "edit-quiz-answer", 1000);
    addDifficultyField(row, question.difficulty);
    editQuizFields.append(row);
  });

  editGuideForm.hidden = false;
  setStatus(editGuideStatus, "");
  editGuideForm.scrollIntoView({ behavior: "smooth", block: "start" });
}

function buildEditedMaterial() {
  return {
    topic: editTopicInput.value.trim(),
    summary: editSummaryInput.value.trim(),
    key_concepts: [...editKeyConceptsFields.querySelectorAll(".edit-concept-row")].map(
      (row) => ({
        name: row.querySelector(".edit-concept-name").value.trim(),
        explanation: row.querySelector(".edit-concept-explanation").value.trim(),
      })
    ),
    flashcards: [...editFlashcardsFields.querySelectorAll(".edit-flashcard-row")].map(
      (row) => ({
        question: row.querySelector(".edit-flashcard-question").value.trim(),
        answer: row.querySelector(".edit-flashcard-answer").value.trim(),
      })
    ),
    quiz_questions: [...editQuizFields.querySelectorAll(".edit-quiz-row")].map(
      (row) => ({
        question: row.querySelector(".edit-quiz-question").value.trim(),
        answer: row.querySelector(".edit-quiz-answer").value.trim(),
        difficulty: row.querySelector(".edit-quiz-difficulty").value,
      })
    ),
  };
}

async function deleteSavedGuide(topicId, title) {
  const confirmed = window.confirm(
    `Delete “${title}”? This permanently removes the guide and its study questions.`
  );
  if (!confirmed) {
    return;
  }

  const token = localStorage.getItem(TOKEN_STORAGE_KEY);
  setStatus(savedGuidesStatus, "Deleting saved study guide...");

  try {
    await sendApiRequest(`/topics/${topicId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });

    if (currentSavedGuide?.id === topicId) {
      currentSavedGuide = null;
      studyResults.hidden = true;
      editGuideForm.hidden = true;
    }

    showSavedGuidesView();
    await loadSavedGuides();
    await loadDashboardLibrary();
    setStatus(savedGuidesStatus, "Study guide deleted.", "success");
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

function logOut() {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
  showAuthenticationForms("You have been logged out.");
}

logoutButton.addEventListener("click", logOut);
accountLogoutButton.addEventListener("click", logOut);

showDashboardButton.addEventListener("click", () => {
  showDashboardHomeView();
  loadDashboardLibrary();
});

showCreateButton.addEventListener("click", showCreateStudyView);

dashboardCreateButton.addEventListener("click", showCreateStudyView);

showSavedButton.addEventListener("click", () => {
  showSavedGuidesView();
  loadSavedGuides();
});

viewAllSavedButton.addEventListener("click", () => {
  showSavedGuidesView();
  loadSavedGuides();
});

showAccountButton.addEventListener("click", showAccountView);

for (const brandLink of document.querySelectorAll('[data-view="dashboard"]')) {
  if (brandLink.tagName === "A") {
    brandLink.addEventListener("click", (event) => {
      event.preventDefault();
      showDashboardHomeView();
      loadDashboardLibrary();
    });
  }
}

mobileMenuButton.addEventListener("click", () => {
  if (appSidebar.classList.contains("open")) closeMobileNavigation();
  else openMobileNavigation();
});
sidebarOverlay.addEventListener("click", closeMobileNavigation);
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closeMobileNavigation();
});

refreshSavedButton.addEventListener("click", loadSavedGuides);

savedSearchForm.addEventListener("submit", (event) => {
  event.preventDefault();
  loadSavedGuides();
});

clearSearchButton.addEventListener("click", () => {
  savedSearchInput.value = "";
  loadSavedGuides();
});

editGuideButton.addEventListener("click", beginEditingCurrentGuide);

deleteOpenGuideButton.addEventListener("click", () => {
  if (currentSavedGuide) {
    deleteSavedGuide(currentSavedGuide.id, currentSavedGuide.topic);
  }
});

cancelEditButton.addEventListener("click", () => {
  editGuideForm.hidden = true;
  setStatus(editGuideStatus, "");
});

editGuideForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!currentSavedGuide) {
    setStatus(editGuideStatus, "Open a saved guide before editing.", "error");
    return;
  }

  const token = localStorage.getItem(TOKEN_STORAGE_KEY);
  const topicId = currentSavedGuide.id;
  updateGuideButton.disabled = true;
  setStatus(editGuideStatus, "Saving your changes...");

  try {
    const updatedGuide = await sendApiRequest(`/topics/${topicId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(buildEditedMaterial()),
    });
    renderStudyMaterial(updatedGuide, { isSaved: true });
    loadDashboardLibrary();
    setStatus(generationStatus, "Saved study guide updated successfully.", "success");
  } catch (error) {
    if (!handleAuthenticationFailure(error)) {
      setStatus(editGuideStatus, error.message, "error");
    }
  } finally {
    updateGuideButton.disabled = false;
  }
});

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
    loadDashboardLibrary();
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
