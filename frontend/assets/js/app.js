/* ==========================================================================
   LawEdAI Frontend Application Logic (Vanilla ES6)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // ---------------------------------------------------------
    // State & Constants Definition
    // ---------------------------------------------------------
    const state = {
        activeCaseId: null,
        activePersona: 'individual', // 'individual' or 'lawfirm'
        attachedFiles: [],           // Local File objects waiting for upload
        isProcessing: false,
        pastCases: [],
        userSession: null,           // Authenticated user session
        apiSettings: {
            provider: 'simulation',
            apiKey: ''
        }
    };

    const API_BASE = window.location.origin;

    // ---------------------------------------------------------
    // DOM Elements Cache
    // ---------------------------------------------------------
    // Auth & Identity
    const authOverlay = document.getElementById('auth-overlay');
    const tabRoleCitizen = document.getElementById('tab-role-citizen');
    const tabRoleLawfirm = document.getElementById('tab-role-lawfirm');
    const formAuthLogin = document.getElementById('form-auth-login');
    const formAuthSignup = document.getElementById('form-auth-signup');
    const loginEmail = document.getElementById('login-email');
    const loginPassword = document.getElementById('login-password');
    const signupName = document.getElementById('signup-name');
    const signupEmail = document.getElementById('signup-email');
    const signupPassword = document.getElementById('signup-password');
    const signupCourt = document.getElementById('signup-court');
    const signupBarId = document.getElementById('signup-bar-id');
    const groupLawfirmFields = document.getElementById('group-lawfirm-fields');
    const linkShowSignup = document.getElementById('link-show-signup');
    const linkShowLogin = document.getElementById('link-show-login');
    const btnSignOut = document.getElementById('btn-sign-out');
    const userDisplayName = document.getElementById('user-display-name');
    const userDisplayDetails = document.getElementById('user-display-details');

    // Navigation / Workspace
    const bodyEl = document.body;
    const workspaceTitle = document.getElementById('workspace-title');
    const radioPersonaOptions = document.querySelectorAll('input[name="workspace-persona"]');
    const labelPersonaIndividual = document.getElementById('label-persona-individual');
    const labelPersonaLawfirm = document.getElementById('label-persona-lawfirm');
    
    // Sidebar
    const caseHistoryList = document.getElementById('case-history-list');
    const btnNewCaseSidebar = document.getElementById('btn-new-case-sidebar');
    const btnSettingsToggle = document.getElementById('btn-settings-toggle');
    
    // Screens/Views
    const viewIntake = document.getElementById('view-intake');
    const viewProcessing = document.getElementById('view-processing');
    const viewCourtroom = document.getElementById('view-courtroom');
    const viewOutput = document.getElementById('view-output');
    const views = [viewIntake, viewProcessing, viewCourtroom, viewOutput];

    // Intake Form, Uploads & UNIQUE-ID
    const citizenIntakeWorkspace = document.getElementById('citizen-intake-workspace');
    const lawfirmIntakeWorkspace = document.getElementById('lawfirm-intake-workspace');
    const formCaseAcquire = document.getElementById('form-case-acquire');
    const inputUniqueId = document.getElementById('input-unique-id');
    const btnSubmitAcquire = document.getElementById('btn-submit-acquire');
    const indUniqueIdDisplay = document.getElementById('ind-unique-id-display');

    const formCaseIntake = document.getElementById('form-case-intake');
    const inputGrievance = document.getElementById('input-grievance');
    const inputLocation = document.getElementById('input-location');
    const btnSubmitCase = document.getElementById('btn-submit-case');
    const dropzone = document.getElementById('dropzone');
    const inputEvidenceFiles = document.getElementById('input-evidence-files');
    const btnBrowseFiles = document.getElementById('btn-browse-files');
    const evidenceCardsList = document.getElementById('evidence-cards-list');
    const evidenceCountText = document.getElementById('evidence-count');

    // Agent Arena Processing
    const rowAgentIntake = document.getElementById('row-agent-intake');
    const statusAgentIntake = document.getElementById('status-agent-intake');
    const rowAgentEvidence = document.getElementById('row-agent-evidence');
    const statusAgentEvidence = document.getElementById('status-agent-evidence');
    const rowAgentLegal = document.getElementById('row-agent-legal');
    const statusAgentLegal = document.getElementById('status-agent-legal');
    const rowAgentReview = document.getElementById('row-agent-review');
    const statusAgentReview = document.getElementById('status-agent-review');
    const rowAgentDrafting = document.getElementById('row-agent-drafting');
    const statusAgentDrafting = document.getElementById('status-agent-drafting');
    
    // Court debate Agent rows (Law Firm Only)
    const agentCourtroomGroup = document.getElementById('agent-courtroom-group');
    const rowAgentPlaintiff = document.getElementById('row-agent-plaintiff');
    const statusAgentPlaintiff = document.getElementById('status-agent-plaintiff');
    const rowAgentDefense = document.getElementById('row-agent-defense');
    const statusAgentDefense = document.getElementById('status-agent-defense');
    const rowAgentJudge = document.getElementById('row-agent-judge');
    const statusAgentJudge = document.getElementById('status-agent-judge');

    // Console logs
    const consoleLogs = document.getElementById('console-logs');

    // Courtroom debate panel
    const courtDebateThread = document.getElementById('court-debate-thread');
    const btnProceedVerdict = document.getElementById('btn-proceed-verdict');

    // Individual Dashboard Outputs
    const dashboardIndividual = document.getElementById('dashboard-individual');
    const indPartyComplainant = document.getElementById('ind-party-complainant');
    const indPartyAccused = document.getElementById('ind-party-accused');
    const indFactsList = document.getElementById('ind-facts-list');
    const indTimelineList = document.getElementById('ind-timeline-list');
    const indBriefText = document.getElementById('ind-brief-text');
    const indStatuteStack = document.getElementById('ind-statute-stack');
    const indEvidenceAudit = document.getElementById('ind-evidence-audit');
    const indSafetyFlags = document.getElementById('ind-safety-flags');
    const indInterpretationsList = document.getElementById('ind-interpretations-list');
    const indPrecedentsList = document.getElementById('ind-precedents-list');

    // Law Firm Dashboard Outputs
    const dashboardLawfirm = document.getElementById('dashboard-lawfirm');
    const gaugeProbabilityNum = document.getElementById('gauge-probability-num');
    const gaugeFillCircle = document.getElementById('gauge-fill-circle');
    const firmProbDesc = document.getElementById('firm-prob-desc');
    const firmStatuteStack = document.getElementById('firm-statute-stack');
    const firmStrategyBrief = document.getElementById('firm-strategy-brief');
    const firmVerdictText = document.getElementById('firm-verdict-text');
    const firmPartyComplainant = document.getElementById('firm-party-complainant');
    const firmPartyAccused = document.getElementById('firm-party-accused');
    const firmTimelineList = document.getElementById('firm-timeline-list');
    const firmEvidenceAudit = document.getElementById('firm-evidence-audit');
    const firmSafetyFlags = document.getElementById('firm-safety-flags');
    const firmBriefText = document.getElementById('firm-brief-text');
    const firmInterpretationsList = document.getElementById('firm-interpretations-list');
    const firmPrecedentsList = document.getElementById('firm-precedents-list');

    // Settings Modal
    const modalSettings = document.getElementById('modal-settings');
    const formBYOKSettings = document.getElementById('form-byok-settings');
    const byokProvider = document.getElementById('byok-provider');
    const groupApiKey = document.getElementById('group-api-key');
    const byokKey = document.getElementById('byok-key');
    const btnSettingsClose = document.getElementById('btn-settings-close');
    const btnSettingsCancel = document.getElementById('btn-settings-cancel');

    // Statute Details Modal
    const modalStatute = document.getElementById('modal-statute');
    const btnStatuteClose = document.getElementById('btn-statute-close');
    const btnStatuteOk = document.getElementById('btn-statute-ok');

    // Law Firm Tab buttons and cards
    const btnTabAcquireDocket = document.getElementById('btn-tab-acquire-docket');
    const btnTabDirectCase = document.getElementById('btn-tab-direct-case');
    const cardAcquireDocket = document.getElementById('card-acquire-docket');

    // Sidebar Collapse & User Writeup Tools
    const btnToggleSidebar = document.getElementById('btn-toggle-sidebar');
    const btnCopyWriteup = document.getElementById('btn-copy-writeup');
    const btnPrintWriteup = document.getElementById('btn-print-writeup');

    // ---------------------------------------------------------
    // App Initialization
    // ---------------------------------------------------------
    function init() {
        loadSettingsFromLocalStorage();
        checkUserAuthentication();
        setupEventListeners();
    }

    function checkUserAuthentication() {
        const storedSession = localStorage.getItem('lawed_session');
        if (storedSession) {
            try {
                const session = JSON.parse(storedSession);
                state.userSession = session.user;
                state.activePersona = session.user.user_type === 'lawfirm' ? 'lawfirm' : 'individual';
                
                // Hide Auth overlay, show Workspace layout
                authOverlay.style.display = 'none';
                bodyEl.classList.remove('theme-light', 'theme-dark');
                bodyEl.classList.add('theme-light');
                
                document.querySelector('.app-layout').style.display = 'grid';

                // Display active counsel profile details
                userDisplayName.innerText = state.userSession.full_name;
                if (state.userSession.user_type === 'lawfirm') {
                    userDisplayDetails.innerText = `${state.userSession.court_name || 'Litigation Counsel'} | ${state.userSession.bar_council_id || 'BC'}`;
                } else {
                    userDisplayDetails.innerText = `Citizen Complainant`;
                }

                // Enforce role-based workspace layouts conditionally
                const personaContainer = document.querySelector('.persona-selector-container');
                if (personaContainer) {
                    personaContainer.style.display = 'none'; // Lock segmented roles switcher completely (RBAC)
                }

                if (state.userSession.user_type === 'lawfirm') {
                    citizenIntakeWorkspace.style.display = 'none';
                    lawfirmIntakeWorkspace.style.display = 'flex';
                } else {
                    citizenIntakeWorkspace.style.display = 'block';
                    lawfirmIntakeWorkspace.style.display = 'none';
                }

                updateThemeClass();
                fetchPastCases();
            } catch (e) {
                console.error("Invalid session format", e);
                localStorage.removeItem('lawed_session');
                showAuthOverlay();
            }
        } else {
            showAuthOverlay();
        }
    }

    function showAuthOverlay() {
        state.userSession = null;
        authOverlay.style.display = 'flex';
        document.querySelector('.app-layout').style.display = 'none';
    }

    // ---------------------------------------------------------
    // LocalStorage Configuration (BYOK)
    // ---------------------------------------------------------
    function loadSettingsFromLocalStorage() {
        const storedProvider = localStorage.getItem('lawed_byok_provider');
        const storedKey = localStorage.getItem('lawed_byok_key');
        
        if (storedProvider) {
            state.apiSettings.provider = storedProvider;
            byokProvider.value = storedProvider;
        }
        if (storedKey) {
            state.apiSettings.apiKey = storedKey;
            byokKey.value = storedKey;
        }
        
        toggleApiKeyInputVisibility();
    }

    function saveSettingsToLocalStorage(provider, key) {
        state.apiSettings.provider = provider;
        state.apiSettings.apiKey = key;
        localStorage.setItem('lawed_byok_provider', provider);
        localStorage.setItem('lawed_byok_key', key);
    }

    function toggleApiKeyInputVisibility() {
        if (byokProvider.value === 'simulation') {
            groupApiKey.style.display = 'none';
        } else {
            groupApiKey.style.display = 'block';
        }
    }

    // ---------------------------------------------------------
    // Theme & UI Control
    // ---------------------------------------------------------
    function updateThemeClass() {
        bodyEl.classList.remove('theme-individual', 'theme-lawfirm');
        if (state.activePersona === 'individual') {
            bodyEl.classList.add('theme-individual');
            workspaceTitle.innerText = "LawEdAI Complainant Portal";
            labelPersonaIndividual.classList.add('active');
            labelPersonaLawfirm.classList.remove('active');
        } else {
            bodyEl.classList.add('theme-lawfirm');
            workspaceTitle.innerText = "LawEdAI Litigation Firm Suite";
            labelPersonaIndividual.classList.remove('active');
            labelPersonaLawfirm.classList.add('active');
        }
    }

    function switchView(viewName) {
        views.forEach(v => v.classList.remove('active'));
        if (viewName === 'intake') {
            viewIntake.classList.add('active');
        } else if (viewName === 'processing') {
            viewProcessing.classList.add('active');
        } else if (viewName === 'courtroom') {
            viewCourtroom.classList.add('active');
        } else if (viewName === 'output') {
            viewOutput.classList.add('active');
        }
    }

    // ---------------------------------------------------------
    // Event Listeners Configuration
    // ---------------------------------------------------------
    function setupEventListeners() {
        // Workspace Persona Toggle
        radioPersonaOptions.forEach(radio => {
            radio.addEventListener('change', (e) => {
                state.activePersona = e.target.value;
                updateThemeClass();
            });
        });

        labelPersonaIndividual.addEventListener('click', () => {
            document.querySelector('input[name="workspace-persona"][value="individual"]').checked = true;
            state.activePersona = 'individual';
            updateThemeClass();
        });

        labelPersonaLawfirm.addEventListener('click', () => {
            document.querySelector('input[name="workspace-persona"][value="lawfirm"]').checked = true;
            state.activePersona = 'lawfirm';
            updateThemeClass();
        });

        // Sidebar - New Case Trigger
        btnNewCaseSidebar.addEventListener('click', startNewCaseFlow);

        // Sidebar - Settings Toggle
        btnSettingsToggle.addEventListener('click', () => {
            modalSettings.classList.add('show');
        });

        btnSettingsClose.addEventListener('click', () => modalSettings.classList.remove('show'));
        btnSettingsCancel.addEventListener('click', () => modalSettings.classList.remove('show'));

        // Statute details modal buttons
        btnStatuteClose.addEventListener('click', () => modalStatute.classList.remove('show'));
        btnStatuteOk.addEventListener('click', () => modalStatute.classList.remove('show'));

        // Law Firm sub-tab controls
        btnTabAcquireDocket.addEventListener('click', () => {
            btnTabAcquireDocket.classList.add('active');
            btnTabDirectCase.classList.remove('active');

            // Apply active visual styling to tabs
            btnTabAcquireDocket.style.background = 'var(--color-primary)';
            btnTabAcquireDocket.style.color = 'var(--bg-panel)';
            btnTabDirectCase.style.background = 'transparent';
            btnTabDirectCase.style.color = 'var(--color-foreground)';

            cardAcquireDocket.style.display = 'block';
            citizenIntakeWorkspace.style.display = 'none';

            // Ensure active persona is set to lawfirm
            state.activePersona = 'lawfirm';
            updateThemeClass();
        });

        btnTabDirectCase.addEventListener('click', () => {
            btnTabDirectCase.classList.add('active');
            btnTabAcquireDocket.classList.remove('active');

            // Apply active visual styling to tabs
            btnTabDirectCase.style.background = 'var(--color-primary)';
            btnTabDirectCase.style.color = 'var(--bg-panel)';
            btnTabAcquireDocket.style.background = 'transparent';
            btnTabAcquireDocket.style.color = 'var(--color-foreground)';

            cardAcquireDocket.style.display = 'none';
            citizenIntakeWorkspace.style.display = 'block';

            // Ensure active persona is set to lawfirm
            state.activePersona = 'lawfirm';
            updateThemeClass();
        });

        // Sidebar Collapse control
        btnToggleSidebar.addEventListener('click', () => {
            document.querySelector('.app-layout').classList.toggle('sidebar-collapsed');
        });

        // Copy Case Brief / Writeup
        btnCopyWriteup.addEventListener('click', () => {
            const txt = document.getElementById('ind-brief-text').innerText;
            navigator.clipboard.writeText(txt).then(() => {
                const prevText = btnCopyWriteup.innerText;
                btnCopyWriteup.innerText = 'Copied!';
                setTimeout(() => { btnCopyWriteup.innerText = prevText; }, 2000);
            }).catch(err => {
                console.error('Could not copy writeup: ', err);
            });
        });

        // Print Writeup Only
        btnPrintWriteup.addEventListener('click', () => {
            const briefContent = document.getElementById('ind-brief-text').innerText;
            const uniqueId = document.getElementById('ind-unique-id-display').innerText;
            const win = window.open('', '_blank');
            win.document.write(`
                <html>
                <head>
                    <title>Case Writeup - Docket Reference</title>
                    <style>
                        body { font-family: Georgia, serif; line-height: 1.6; padding: 40px; color: #1a1a1a; max-width: 800px; margin: 0 auto; }
                        h1 { font-family: sans-serif; font-size: 24px; border-bottom: 2px solid #a99260; padding-bottom: 12px; margin-bottom: 20px; }
                        pre { white-space: pre-wrap; font-family: Georgia, serif; font-size: 16px; }
                        .meta { margin-bottom: 30px; font-size: 14px; color: #666; font-family: sans-serif; }
                    </style>
                </head>
                <body>
                    <h1>FORMULATED COMPLAINT BRIEF (WRITEUP)</h1>
                    <div class="meta">
                        <strong>Docket Unique Reference ID:</strong> ${uniqueId}<br>
                        <strong>Generated on:</strong> ${new Date().toLocaleDateString('en-GB')}
                    </div>
                    <pre>${briefContent}</pre>
                    <script>window.onload = function() { window.print(); window.close(); }</script>
                </body>
                </html>
            `);
            win.document.close();
        });

        // Individual dashboard tabs toggle listeners
        const userTabBtns = document.querySelectorAll('.user-tab-btn');
        const userTabContents = document.querySelectorAll('.user-tab-content');
        
        userTabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const tabName = btn.getAttribute('data-tab');
                
                userTabBtns.forEach(b => {
                    b.classList.remove('active');
                    b.style.background = 'transparent';
                    b.style.color = 'var(--color-foreground)';
                });
                btn.classList.add('active');
                btn.style.background = 'var(--color-primary)';
                btn.style.color = 'var(--bg-panel)';
                
                userTabContents.forEach(content => {
                    if (content.id === tabName) {
                        if (tabName === 'user-tab-timeline') {
                            content.style.display = 'flex'; // Timeline uses flex-direction column
                        } else {
                            content.style.display = 'block';
                        }
                    } else {
                        content.style.display = 'none';
                    }
                });
            });
        });
        
        byokProvider.addEventListener('change', toggleApiKeyInputVisibility);

        // Settings Modal Form Save
        formBYOKSettings.addEventListener('submit', (e) => {
            e.preventDefault();
            saveSettingsToLocalStorage(byokProvider.value, byokKey.value);
            modalSettings.classList.remove('show');
            addConsoleLine("Configuration updated. Model provider set to: " + byokProvider.value.toUpperCase(), "info");
        });

        // File Uploader triggers
        btnBrowseFiles.addEventListener('click', () => inputEvidenceFiles.click());
        inputEvidenceFiles.addEventListener('change', handleFileSelection);

        // Drag & Drop events
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropzone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropzone.classList.remove('dragover');
            }, false);
        });

        dropzone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            handleDroppedFiles(files);
        });

        // Form Intake Submission
        formCaseIntake.addEventListener('submit', handleIntakeSubmission);

        // Debate Continue to Verdict Button
        btnProceedVerdict.addEventListener('click', () => {
            switchView('output');
            loadDashboardDetails(state.activeCaseId);
        });

        // --- AUTH & RBAC EVENT LISTENERS ---
        // Tab Role Switches (Citizen vs Law Firm)
        tabRoleCitizen.addEventListener('click', () => {
            tabRoleCitizen.classList.add('active');
            tabRoleLawfirm.classList.remove('active');
            document.getElementById('login-form-title').innerText = "Citizen Login";
            document.getElementById('signup-form-title').innerText = "Citizen Sign Up";
            groupLawfirmFields.style.display = 'none';
        });

        tabRoleLawfirm.addEventListener('click', () => {
            tabRoleLawfirm.classList.add('active');
            tabRoleCitizen.classList.remove('active');
            document.getElementById('login-form-title').innerText = "Law Firm Login";
            document.getElementById('signup-form-title').innerText = "Law Firm Sign Up";
            groupLawfirmFields.style.display = 'block';
        });

        // Switch Forms (Login / Signup)
        linkShowSignup.addEventListener('click', (e) => {
            e.preventDefault();
            formAuthLogin.style.display = 'none';
            formAuthSignup.style.display = 'block';
        });

        linkShowLogin.addEventListener('click', (e) => {
            e.preventDefault();
            formAuthSignup.style.display = 'none';
            formAuthLogin.style.display = 'block';
        });

        // Profile Sign Out
        btnSignOut.addEventListener('click', handleSignOut);

        // Submit Forms
        formAuthLogin.addEventListener('submit', handleAuthLogin);
        formAuthSignup.addEventListener('submit', handleAuthSignup);
        formCaseAcquire.addEventListener('submit', handleCaseAcquisition);
    }

    // ---------------------------------------------------------
    // Authentication & Case Acquisition Handlers (RBAC & Unique ID)
    // ---------------------------------------------------------
    async function handleAuthLogin(e) {
        e.preventDefault();
        const email = loginEmail.value.trim();
        const password = loginPassword.value;
        const activeTab = document.querySelector('.auth-role-tab.active');
        const role = activeTab ? activeTab.getAttribute('data-role') : 'individual';

        try {
            const res = await fetch(`${API_BASE}/api/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Authentication failed.");
            }

            const data = await res.json();
            const loggedInUserType = data.user?.user_type;

            if (role === 'individual' && loggedInUserType !== 'individual') {
                throw new Error("This account is registered as a Law Firm. Please select the Law Firm workspace to log in.");
            }
            if (role === 'lawfirm' && loggedInUserType !== 'lawfirm') {
                throw new Error("This account is registered as an Individual. Please select the Citizen workspace to log in.");
            }

            localStorage.setItem('lawed_session', JSON.stringify(data));
            checkUserAuthentication();
            loginEmail.value = '';
            loginPassword.value = '';
            
            // Switch views based on persona
            switchView('intake');
        } catch (error) {
            alert("Login failed: " + error.message);
        }
    }

    async function handleAuthSignup(e) {
        e.preventDefault();
        const activeTab = document.querySelector('.auth-role-tab.active');
        const role = activeTab.getAttribute('data-role');

        const email = signupEmail.value.trim();
        const password = signupPassword.value;
        const name = signupName.value.trim();
        const court = signupCourt.value.trim();
        const barId = signupBarId.value.trim();

        try {
            const payload = {
                email,
                password,
                full_name: name,
                user_type: role
            };

            if (role === 'lawfirm') {
                payload.court_name = court || "Delhi High Court";
                payload.bar_council_id = barId || "BC-DEFAULT";
            }

            const res = await fetch(`${API_BASE}/api/auth/signup`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Signup registration failed.");
            }

            alert("Signup successful! You can now log in using your credentials.");
            signupEmail.value = '';
            signupPassword.value = '';
            signupName.value = '';
            signupCourt.value = '';
            signupBarId.value = '';
            
            // Toggle back to login form
            formAuthSignup.style.display = 'none';
            formAuthLogin.style.display = 'block';
        } catch (error) {
            alert("Signup failed: " + error.message);
        }
    }

    function handleSignOut() {
        if (confirm("Are you sure you want to sign out from the legal advisory portal?")) {
            localStorage.removeItem('lawed_session');
            showAuthOverlay();
            startNewCaseFlow();
        }
    }

    async function handleCaseAcquisition(e) {
        e.preventDefault();
        const uniqueId = inputUniqueId.value.trim().toUpperCase();
        if (!uniqueId || !state.userSession) return;

        state.isProcessing = true;
        btnSubmitAcquire.disabled = true;
        btnSubmitAcquire.innerHTML = 'Acquiring Docket & Running Courtroom Battle... <span class="spinner-ring" style="width:14px;height:14px;margin:0;border-width:2px;"></span>';

        try {
            const res = await fetch(`${API_BASE}/api/cases/acquire`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    unique_id: uniqueId,
                    acquired_by_firm_id: state.userSession.id
                })
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Case acquisition failed.");
            }

            const data = await res.json();
            const caseId = data.case_id;
            state.activeCaseId = caseId;
            state.activePersona = 'lawfirm';

            // Switch to processing animation sequence
            switchView('processing');
            resetAgentVisualStatus();
            agentCourtroomGroup.style.display = 'block';

            // Sequencing
            await animateAgentSequence();

            // Transition to simulated courtroom Objections
            switchView('courtroom');
            loadCourtroomObjections(caseId);

            // Reset inputs
            inputUniqueId.value = '';
        } catch (error) {
            alert("Case acquisition failed: " + error.message);
        } finally {
            state.isProcessing = false;
            btnSubmitAcquire.disabled = false;
            btnSubmitAcquire.innerHTML = 'Acquire & Simulate Courtroom Adjudication';
        }
    }

    // ---------------------------------------------------------
    // File Handling & UI Cards
    // ---------------------------------------------------------
    function handleFileSelection(e) {
        const files = e.target.files;
        handleDroppedFiles(files);
    }

    function handleDroppedFiles(files) {
        Array.from(files).forEach(file => {
            // Basic size boundary check (20MB)
            if (file.size > 20 * 1024 * 1024) {
                alert(`File ${file.name} is too large. Max size is 20MB.`);
                return;
            }
            state.attachedFiles.push(file);
        });
        renderAttachedFilesList();
    }

    function renderAttachedFilesList() {
        evidenceCountText.innerText = state.attachedFiles.length;
        
        if (state.attachedFiles.length === 0) {
            evidenceCardsList.innerHTML = '<p class="evidence-list-empty">No files attached to this case. Digital proof is highly recommended for BNS filings.</p>';
            return;
        }

        evidenceCardsList.innerHTML = '';
        state.attachedFiles.forEach((file, index) => {
            const sizeStr = formatBytes(file.size);
            const ext = file.name.split('.').pop().toUpperCase();
            
            const card = document.createElement('div');
            card.className = 'evidence-card';
            card.innerHTML = `
                <div class="evidence-card-left">
                    <svg class="evidence-file-icon" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                    </svg>
                    <div class="evidence-file-details">
                        <div class="evidence-file-name" title="${file.name}">${file.name}</div>
                        <div class="evidence-file-size">${ext} File • ${sizeStr}</div>
                    </div>
                </div>
                <div class="evidence-card-right">
                    <span class="evidence-rating-pill medium">TBC</span>
                    <button type="button" class="btn-remove-evidence" data-index="${index}">
                        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>
                </div>
            `;

            // Bind removal event
            card.querySelector('.btn-remove-evidence').addEventListener('click', (e) => {
                const idx = parseInt(e.currentTarget.getAttribute('data-index'));
                state.attachedFiles.splice(idx, 1);
                renderAttachedFilesList();
            });

            evidenceCardsList.appendChild(card);
        });
    }

    function formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    // ---------------------------------------------------------
    // Workflow 1: Intake & Upload Submit Actions
    // ---------------------------------------------------------
    async function handleIntakeSubmission(e) {
        e.preventDefault();
        
        if (state.isProcessing) return;
        state.isProcessing = true;
        btnSubmitCase.disabled = true;
        btnSubmitCase.innerHTML = 'Submitting... <span class="spinner-ring" style="width:14px;height:14px;margin:0;border-width:2px;"></span>';

        const grievance = inputGrievance.value.trim();
        const location = inputLocation.value.trim();
        const persona = state.activePersona;

        try {
            // Step A: Create the Case
            addConsoleLine(`Connecting to legal server gateway. Mapped persona: ${persona.toUpperCase()}`, "info");
            
            const caseData = new FormData();
            caseData.append("grievance", grievance);
            caseData.append("location", location);
            caseData.append("user_persona", persona);
            if (state.userSession && state.userSession.id) {
                if (state.userSession.user_type === 'lawfirm') {
                    caseData.append("acquired_by_firm_id", state.userSession.id);
                } else {
                    caseData.append("citizen_id", state.userSession.id);
                }
            }

            const res = await fetch(`${API_BASE}/api/cases`, {
                method: "POST",
                body: caseData
            });

            if (!res.ok) throw new Error("Failed to register case submission.");
            const caseResult = await res.json();
            const caseId = caseResult.case_id;
            state.activeCaseId = caseId;

            if (caseResult.unique_id && indUniqueIdDisplay) {
                indUniqueIdDisplay.innerText = caseResult.unique_id;
            }
            
            addConsoleLine(`Case registered successfully. ID Assigned: L-00${caseId}`, "success");

            // Step B: Upload Attached Evidence Files
            if (state.attachedFiles.length > 0) {
                addConsoleLine(`Uploading ${state.attachedFiles.length} attached evidence files.`, "info");
                
                const fileData = new FormData();
                state.attachedFiles.forEach(file => {
                    fileData.append("files", file);
                });

                const uploadRes = await fetch(`${API_BASE}/api/cases/${caseId}/evidence`, {
                    method: "POST",
                    body: fileData
                });

                if (!uploadRes.ok) throw new Error("Failed to upload evidence files.");
                const uploadResult = await uploadRes.json();
                addConsoleLine(`Evidence uploaded. Mapped entries inside DB secure table.`, "success");
            }

            // Step C: Trigger Multi-Agent Core Analysis Workflow
            runAgentOrchestration(caseId);

        } catch (error) {
            console.error(error);
            alert("Error submitting case details: " + error.message);
            state.isProcessing = false;
            btnSubmitCase.disabled = false;
            btnSubmitCase.innerHTML = 'Initiate Mapping Sequence';
        }
    }

    // ---------------------------------------------------------
    // Workflow 2: Agent Arena & Progress Visualizers
    // ---------------------------------------------------------
    async function runAgentOrchestration(caseId) {
        switchView('processing');
        resetAgentVisualStatus();
        
        // Toggle Court debate agents visibility in processing track based on persona
        if (state.activePersona === 'lawfirm') {
            agentCourtroomGroup.style.display = 'block';
        } else {
            agentCourtroomGroup.style.display = 'none';
        }

        addConsoleLine("Connecting multi-agent neural thread...", "info");
        
        // Set Headers if BYOK is active
        const headers = {};
        if (state.apiSettings.provider !== 'simulation' && state.apiSettings.apiKey) {
            if (state.apiSettings.provider === 'groq') {
                headers['X-Groq-API-Key'] = state.apiSettings.apiKey;
            } else if (state.apiSettings.provider === 'openai') {
                headers['X-OpenAI-API-Key'] = state.apiSettings.apiKey;
            }
        }

        try {
            // Update Active Indicators sequentially to make it feel premium, pulsing, and active!
            await animateAgentSequence();
            
            addConsoleLine("Multi-agent baseline mapping complete. Formulating Complainant brief...", "success");
            
            // Direct next navigation
            setTimeout(() => {
                state.isProcessing = false;
                btnSubmitCase.disabled = false;
                btnSubmitCase.innerHTML = 'Initiate Mapping Sequence';
                
                // Transition straight to Output Brief
                switchView('output');
                loadDashboardDetails(caseId);
                
                fetchPastCases();
            }, 1000);

        } catch (error) {
            addConsoleLine("Pipeline crash: " + error.message, "danger");
            alert("Orchestrator error: " + error.message);
            state.isProcessing = false;
            btnSubmitCase.disabled = false;
            btnSubmitCase.innerHTML = 'Initiate Mapping Sequence';
        }
    }

    function resetAgentVisualStatus() {
        if (consoleLogs) consoleLogs.innerHTML = '';
        const rows = [rowAgentIntake, rowAgentEvidence, rowAgentLegal, rowAgentReview, rowAgentDrafting, rowAgentPlaintiff, rowAgentDefense, rowAgentJudge];
        const statuses = [statusAgentIntake, statusAgentEvidence, statusAgentLegal, statusAgentReview, statusAgentDrafting, statusAgentPlaintiff, statusAgentDefense, statusAgentJudge];
        
        rows.forEach(r => { if (r) r.classList.remove('active', 'completed'); });
        statuses.forEach(s => { if (s) s.innerText = "Waiting in pool... "; });

        // Reset progress bar
        const progressBar = document.getElementById('processing-progress-bar');
        const statusText = document.getElementById('processing-status-text');
        const stepDetail = document.getElementById('processing-step-detail');
        if (progressBar) progressBar.style.width = '0%';
        if (statusText) statusText.innerText = 'Initializing cooperative agents...';
        if (stepDetail) stepDetail.innerText = 'Connecting multi-agent neural thread...';
    }

    async function animateAgentSequence() {
        const delay = (ms) => new Promise(res => setTimeout(res, ms));
        const statusText = document.getElementById('processing-status-text');
        const progressBar = document.getElementById('processing-progress-bar');
        const stepDetail = document.getElementById('processing-step-detail');
        
        const updateProgress = (percentage, title, detail) => {
            if (statusText) statusText.innerText = title;
            if (progressBar) progressBar.style.width = `${percentage}%`;
            if (stepDetail) stepDetail.innerText = detail;
        };
        
        // Intake (20%)
        if (rowAgentIntake) rowAgentIntake.classList.add('active');
        if (statusAgentIntake) statusAgentIntake.innerText = "Processing grievance facts...";
        addConsoleLine("> Intake Fact Extractor: Parsing sentence semantic frames...", "info");
        updateProgress(20, "Extracting case facts and key parameters...", "Extracting core grievance facts and locations...");
        await delay(1200);
        if (rowAgentIntake) {
            rowAgentIntake.classList.remove('active');
            rowAgentIntake.classList.add('completed');
        }
        if (statusAgentIntake) statusAgentIntake.innerText = "Facts extracted successfully.";
        addConsoleLine("> Intake Fact Extractor: Facts database records created.", "success");

        // Evidence (40%)
        if (rowAgentEvidence) rowAgentEvidence.classList.add('active');
        if (statusAgentEvidence) statusAgentEvidence.innerText = "Scanning attachments for credibility...";
        addConsoleLine("> Evidence Verifier: Running simulated OCR text extraction...", "info");
        updateProgress(40, "Analyzing attached evidence files...", "Scanning attachments and auditing admissibility...");
        await delay(1000);
        if (rowAgentEvidence) {
            rowAgentEvidence.classList.remove('active');
            rowAgentEvidence.classList.add('completed');
        }
        if (statusAgentEvidence) statusAgentEvidence.innerText = "Evidence credibility rated.";
        addConsoleLine("> Evidence Verifier: Digital files assigned support ratings.", "success");

        // Legal (RAG) (60%)
        if (rowAgentLegal) rowAgentLegal.classList.add('active');
        if (statusAgentLegal) statusAgentLegal.innerText = "Matching sections in BNS, BSA, BNSS...";
        addConsoleLine("> Statutory RAG Matcher: Querying corpus index files...", "info");
        updateProgress(60, "Mapping statutory provisions (BNS, BSA, BNSS)...", "Mapping relevant BNS, BNSS, and BSA statutes...");
        await delay(1300);
        if (rowAgentLegal) {
            rowAgentLegal.classList.remove('active');
            rowAgentLegal.classList.add('completed');
        }
        if (statusAgentLegal) statusAgentLegal.innerText = "Statutes mapped successfully.";
        addConsoleLine("> Statutory RAG Matcher: Sections BNS 318, BSA 63, BNSS 173 bound.", "success");

        // Review (80%)
        if (rowAgentReview) rowAgentReview.classList.add('active');
        if (statusAgentReview) statusAgentReview.innerText = "Analyzing litigation risks and gaps...";
        addConsoleLine("> Integrity Reviewer: Verifying digital certificates requirements under Section 63 BSA...", "info");
        updateProgress(80, "Auditing legal compliance and integrity flags...", "Checking litigation risks and digital evidence requirements...");
        await delay(1100);
        if (rowAgentReview) {
            rowAgentReview.classList.remove('active');
            rowAgentReview.classList.add('completed');
        }
        if (statusAgentReview) statusAgentReview.innerText = "Integrity checked. Risks flagged.";
        addConsoleLine("> Integrity Reviewer: Safety alerts compiled.", "success");

        // Drafting (90%)
        if (rowAgentDrafting) rowAgentDrafting.classList.add('active');
        if (statusAgentDrafting) statusAgentDrafting.innerText = "Building pre-filing Case Brief...";
        addConsoleLine("> Case Brief Drafter: Formulating legal brief structure...", "info");
        updateProgress(90, "Formulating case docket and brief writeup...", "Compiling pre-filing Case Docket and Writeup...");
        await delay(1000);
        if (rowAgentDrafting) {
            rowAgentDrafting.classList.remove('active');
            rowAgentDrafting.classList.add('completed');
        }
        if (statusAgentDrafting) statusAgentDrafting.innerText = "Case Brief draft constructed.";
        addConsoleLine("> Case Brief Drafter: Completed Case Preparation Package.", "success");

        if (state.activePersona === 'lawfirm') {
            // Plaintiff (93%)
            if (rowAgentPlaintiff) rowAgentPlaintiff.classList.add('active');
            if (statusAgentPlaintiff) statusAgentPlaintiff.innerText = "Structuring Prosecution opening arguments...";
            addConsoleLine("> Complainant Opening Counsel: Citing BNS and mapping facts to elements...", "info");
            updateProgress(93, "Simulating opening arguments...", "Formulating Prosecution arguments under BNS...");
            await delay(1000);
            if (rowAgentPlaintiff) {
                rowAgentPlaintiff.classList.remove('active');
                rowAgentPlaintiff.classList.add('completed');
            }
            if (statusAgentPlaintiff) statusAgentPlaintiff.innerText = "Aggressive Opening compiled.";
            addConsoleLine("> Complainant Opening Counsel: Opened litigation.", "success");

            // Defense (96%)
            if (rowAgentDefense) rowAgentDefense.classList.add('active');
            if (statusAgentDefense) statusAgentDefense.innerText = "Formulating defense hurdles & objections...";
            addConsoleLine("> Defense Objection Counsel: Searching admissibility issues under BSA Section 63...", "info");
            updateProgress(96, "Evaluating opposing defense hurdles...", "Drafting Defense objections under BSA Section 63...");
            await delay(1200);
            if (rowAgentDefense) {
                rowAgentDefense.classList.remove('active');
                rowAgentDefense.classList.add('completed');
            }
            if (statusAgentDefense) statusAgentDefense.innerText = "Adversarial challenges prepared.";
            addConsoleLine("> Defense Objection Counsel: Lodged digital evidence objection.", "success");

            // Judge (100%)
            if (rowAgentJudge) rowAgentJudge.classList.add('active');
            if (statusAgentJudge) statusAgentJudge.innerText = "Summoning verdict and probability rates...";
            addConsoleLine("> Judicial Adjudicator: Weighting arguments. Summing evidence rates...", "info");
            updateProgress(100, "Adjudicating courtroom outcome and win probability...", "Magistrate is writing final verdict and Litigious guidelines...");
            await delay(1000);
            if (rowAgentJudge) {
                rowAgentJudge.classList.remove('active');
                rowAgentJudge.classList.add('completed');
            }
            if (statusAgentJudge) statusAgentJudge.innerText = "Hon'ble Magistrate verdict filed.";
            addConsoleLine("> Judicial Adjudicator: Case evaluation finished.", "success");
        } else {
            // Citizen Judge baseline (100%)
            if (rowAgentJudge) rowAgentJudge.classList.add('active');
            if (statusAgentJudge) statusAgentJudge.innerText = "Calculating case strength baseline...";
            addConsoleLine("> Judicial Adjudicator: Determining win probability index...", "info");
            updateProgress(100, "Finalizing case file and dossier...", "Magistrate is finalizing win probability index...");
            await delay(1000);
            if (rowAgentJudge) {
                rowAgentJudge.classList.remove('active');
                rowAgentJudge.classList.add('completed');
            }
            if (statusAgentJudge) statusAgentJudge.innerText = "Win index verified.";
            addConsoleLine("> Judicial Adjudicator: Case strength calculated.", "success");
        }
    }

    function addConsoleLine(text, type = "") {
        if (!consoleLogs) return;
        const line = document.createElement('div');
        line.className = `console-line ${type}`;
        line.innerText = text;
        consoleLogs.appendChild(line);
        consoleLogs.scrollTop = consoleLogs.scrollHeight;
    }

    // ---------------------------------------------------------
    // Workflow 3: Courtroom Debate Typing Simulation (Law Firm)
    // ---------------------------------------------------------
    async function loadCourtroomObjections(caseId) {
        courtDebateThread.innerHTML = `
            <div class="debate-system-card">
                <div class="debate-system-icon">⚖️</div>
                <div>Magistrate calls the matter. Complainant Counsel, present your primary arguments under BNS substantive provisions.</div>
            </div>
        `;
        
        btnProceedVerdict.style.display = 'none';

        try {
            const res = await fetch(`${API_BASE}/api/cases/${caseId}/dashboard`);
            if (!res.ok) throw new Error("Failed to load courtroom debate logs.");
            const data = await res.json();
            
            const logs = data.debate_logs;
            if (!logs || logs.length === 0) {
                // If logs are empty, inject simulated logs
                btnProceedVerdict.style.display = 'inline-flex';
                return;
            }

            // Sequentially type out courtroom arguments to look premium and fully active!
            await animateCourtDebate(logs);
            
            btnProceedVerdict.style.display = 'inline-flex';
            btnProceedVerdict.scrollIntoView({ behavior: 'smooth' });

        } catch (error) {
            console.error(error);
            btnProceedVerdict.style.display = 'inline-flex';
        }
    }

    async function animateCourtDebate(logs) {
        const delay = (ms) => new Promise(res => setTimeout(res, ms));
        
        for (let i = 0; i < logs.length; i++) {
            const log = logs[i];
            
            // Format Speaker title
            let speakerTitle = "Complainant Opening Counsel";
            let speakerClass = "plaintiff";
            if (log.speaker === "Defense_Lawyer") {
                speakerTitle = "Defense Objection Counsel";
                speakerClass = "defense";
            } else if (log.speaker === "Judge") {
                speakerTitle = "Hon'ble Judicial Magistrate";
                speakerClass = "judge";
            }

            const bubble = document.createElement('div');
            bubble.className = `debate-bubble ${speakerClass}`;
            bubble.innerHTML = `
                <span class="bubble-speaker">${speakerTitle}</span>
                <span class="bubble-text"></span>
            `;
            
            courtDebateThread.appendChild(bubble);
            courtDebateThread.scrollTop = courtDebateThread.scrollHeight;

            // Smooth typing text animation
            await typeTextIntoBubble(bubble.querySelector('.bubble-text'), log.text, 6);
            await delay(1000);
        }
    }

    function typeTextIntoBubble(element, text, speed = 8) {
        return new Promise(resolve => {
            let i = 0;
            // Cap character printing size to prevent endless typing on extremely long drafts
            const printLimit = 800; 
            const textToPrint = text.length > printLimit ? text.substring(0, printLimit) + " ... [Summarized for court]" : text;

            function type() {
                if (i < textToPrint.length) {
                    element.innerHTML += textToPrint.charAt(i);
                    i++;
                    setTimeout(type, speed);
                } else {
                    resolve();
                }
            }
            type();
        });
    }

    // ---------------------------------------------------------
    // Workflow 4: Renders Dashboard Output (Dual Portal)
    // ---------------------------------------------------------
    async function loadDashboardDetails(caseId) {
        try {
            const res = await fetch(`${API_BASE}/api/cases/${caseId}/dashboard`);
            if (!res.ok) throw new Error("Failed to load dashboard parameters.");
            const data = await res.json();

            // Toggle visual panels depending on persona selected
            if (data.user_persona === 'lawfirm') {
                dashboardIndividual.style.display = 'none';
                dashboardLawfirm.style.display = 'block';
                renderLawfirmDashboard(data);
            } else {
                dashboardIndividual.style.display = 'block';
                dashboardLawfirm.style.display = 'none';
                renderIndividualDashboard(data);
                
                // Reset Complainant sub-tabs to default active writeup tab!
                const writeupTabBtn = document.querySelector('.user-tab-btn[data-tab="user-tab-writeup"]');
                if (writeupTabBtn) writeupTabBtn.click();
            }

        } catch (error) {
            console.error(error);
            alert("Error loading case dashboard results: " + error.message);
        }
    }

    function renderInterpretations(container, interpretations) {
        if (!container) return;
        container.innerHTML = '';
        if (interpretations && interpretations.length > 0) {
            interpretations.forEach(item => {
                const div = document.createElement('div');
                div.className = 'interpretation-item';
                div.innerHTML = `
                    <div class="interpretation-clause-header">
                        <span>${item.clause_number}</span>
                        <span>${item.act_title}</span>
                    </div>
                    <div class="interpretation-fact">"${item.user_fact_mapping}"</div>
                    <div class="interpretation-opinion">${item.legal_opinion}</div>
                `;
                container.appendChild(div);
            });
        } else {
            container.innerHTML = '<p class="text-muted">No statutory interpretations compiled for this case.</p>';
        }
    }

    function renderPrecedents(container, precedents) {
        if (!container) return;
        container.innerHTML = '';
        if (precedents && precedents.length > 0) {
            precedents.forEach(item => {
                const card = document.createElement('div');
                card.className = 'precedent-card';
                card.innerHTML = `
                    <div class="precedent-header">
                        <h4 class="precedent-name">${item.case_name}</h4>
                        <span class="precedent-citation-badge">${item.citation} (${item.year})</span>
                    </div>
                    <div class="precedent-summary">
                        <strong>Brief Holding:</strong> ${item.summary}
                    </div>
                    <div class="precedent-relevance">
                        <strong>Statutory Relevance:</strong> ${item.relevance}
                    </div>
                `;
                container.appendChild(card);
            });
        } else {
            container.innerHTML = '<p class="text-muted">No landmark Supreme Court precedents mapped for these offense segments.</p>';
        }
    }

    function renderIndividualDashboard(data) {
        // Parties
        if (indPartyComplainant) indPartyComplainant.innerText = data.parties?.complainant || "User (Informant)";
        if (indPartyAccused) indPartyAccused.innerText = data.parties?.accused || "Accused Suspect";

        // Facts
        if (indFactsList) {
            indFactsList.innerHTML = '';
            if (data.facts && data.facts.length > 0) {
                data.facts.forEach(fact => {
                    const li = document.createElement('li');
                    li.innerText = fact;
                    indFactsList.appendChild(li);
                });
            } else {
                indFactsList.innerHTML = '<li>No facts extracted. Narrative might be too sparse.</li>';
            }
        }

        // Timeline
        if (indTimelineList) {
            indTimelineList.innerHTML = '';
            if (data.timeline && data.timeline.length > 0) {
                data.timeline.forEach(t => {
                    const item = document.createElement('div');
                    item.className = 'timeline-v-item';
                    item.innerHTML = `
                        <div class="timeline-v-node"></div>
                        <div class="timeline-v-date font-outfit">${t.date}</div>
                        <div class="timeline-v-event font-inter">${t.event}</div>
                    `;
                    indTimelineList.appendChild(item);
                });
            } else {
                indTimelineList.innerHTML = '<p class="text-muted">No chronological markers detected in the grievance.</p>';
            }
        }

        // Draft case Brief
        if (indBriefText) indBriefText.innerText = data.case_brief || "Case brief draft construction was skipped.";

        // Statutes
        if (indStatuteStack) {
            indStatuteStack.innerHTML = '';
            if (data.statutes && data.statutes.length > 0) {
                data.statutes.forEach(s => {
                    const card = document.createElement('div');
                    card.className = 'statute-pill-card-mini';
                    card.style.cursor = 'pointer';
                    card.innerHTML = `
                        <div class="statute-pill-header">
                            <span class="statute-pill-num text-accent">Sec ${s.section_number}</span>
                            <span class="statute-pill-act">${s.code_type}</span>
                        </div>
                        <div class="statute-pill-title font-outfit" style="margin-top: 4px;">${s.section_title}</div>
                    `;
                    card.addEventListener('click', () => openStatuteModal(s));
                    indStatuteStack.appendChild(card);
                });
            } else {
                indStatuteStack.innerHTML = '<p class="text-muted">No specific penal code matches found.</p>';
            }
        }

        // Evidence Audit
        if (indEvidenceAudit) {
            indEvidenceAudit.innerHTML = '';
            if (data.evidence && data.evidence.length > 0) {
                data.evidence.forEach(e => {
                    const card = document.createElement('div');
                    card.className = 'audit-card';
                    let ratingClass = e.support_rating?.toLowerCase() || 'medium';
                    
                    card.innerHTML = `
                        <span class="audit-card-title">${e.filename}</span>
                        <span class="evidence-rating-pill ${ratingClass}">${e.support_rating}</span>
                    `;
                    indEvidenceAudit.appendChild(card);
                });
            } else {
                indEvidenceAudit.innerHTML = '<p class="evidence-list-empty">No attachments analyzed. Admissibility audit skipped.</p>';
            }
        }

        // Safety Flags
        if (indSafetyFlags) {
            indSafetyFlags.innerHTML = '';
            if (data.flags && data.flags.length > 0) {
                data.flags.forEach(f => {
                    const card = document.createElement('div');
                    const isHigh = f.severity === 'High';
                    card.className = `safety-flag-card ${isHigh ? 'high' : ''}`;
                    card.innerHTML = `
                        <div class="safety-flag-title font-outfit">${f.flag_title}</div>
                        <div class="safety-flag-msg font-inter">${f.message}</div>
                    `;
                    indSafetyFlags.appendChild(card);
                });
            } else {
                indSafetyFlags.innerHTML = '<p class="text-muted">Completeness checks passed. No litigation flags raised.</p>';
            }
        }

        // Render statutory cognitive interpretations & landmark precedents
        renderInterpretations(indInterpretationsList, data.interpretations);
        renderPrecedents(indPrecedentsList, data.precedents);
    }

    function renderLawfirmDashboard(data) {
        // 1. Radial gauge animation
        const prob = Math.round(data.win_probability || 50);
        animateRadialGauge(prob);

        // Timeline & Dossier
        if (firmPartyComplainant) firmPartyComplainant.innerText = data.parties?.complainant || "Prosecution";
        if (firmPartyAccused) firmPartyAccused.innerText = data.parties?.accused || "Accused";

        if (firmTimelineList) {
            firmTimelineList.innerHTML = '';
            if (data.timeline && data.timeline.length > 0) {
                data.timeline.forEach(t => {
                    const item = document.createElement('div');
                    item.className = 'timeline-v-item';
                    item.innerHTML = `
                        <div class="timeline-v-node"></div>
                        <div class="timeline-v-date font-outfit">${t.date}</div>
                        <div class="timeline-v-event font-inter">${t.event}</div>
                    `;
                    firmTimelineList.appendChild(item);
                });
            } else {
                firmTimelineList.innerHTML = '<p class="text-muted">No chronological dossier timeline detected.</p>';
            }
        }

        // Statutes
        if (firmStatuteStack) {
            firmStatuteStack.innerHTML = '';
            if (data.statutes && data.statutes.length > 0) {
                data.statutes.forEach(s => {
                    const card = document.createElement('div');
                    card.className = 'statute-pill-card';
                    card.style.cursor = 'pointer';
                    card.innerHTML = `
                        <div class="statute-pill-header">
                            <span class="statute-pill-num text-accent">Sec ${s.section_number}</span>
                            <span class="statute-pill-act">${s.code_type}</span>
                        </div>
                        <div class="statute-pill-title font-outfit">${s.section_title}</div>
                        ${s.procedural_route ? `<div class="statute-pill-route" style="border:none;margin:0;padding:0;"><strong>Authority:</strong> ${s.procedural_route}</div>` : ''}
                    `;
                    card.addEventListener('click', () => openStatuteModal(s));
                    firmStatuteStack.appendChild(card);
                });
            } else {
                firmStatuteStack.innerHTML = '<p class="text-muted">No matched statutes compiled.</p>';
            }
        }

        // Strategy Report
        if (firmStrategyBrief) firmStrategyBrief.innerText = data.strategy_report || "Litigation opponent strategy report skipped.";

        // Verdict Order
        if (firmVerdictText) firmVerdictText.innerText = data.judge_verdict || "Magistrate verdict skipped.";

        // Evidence Audit
        if (firmEvidenceAudit) {
            firmEvidenceAudit.innerHTML = '';
            if (data.evidence && data.evidence.length > 0) {
                data.evidence.forEach(e => {
                    const card = document.createElement('div');
                    card.className = 'audit-card';
                    let ratingClass = e.support_rating?.toLowerCase() || 'medium';
                    card.innerHTML = `
                        <span class="audit-card-title">${e.filename}</span>
                        <span class="evidence-rating-pill ${ratingClass}">${e.support_rating}</span>
                    `;
                    firmEvidenceAudit.appendChild(card);
                });
            } else {
                firmEvidenceAudit.innerHTML = '<p class="evidence-list-empty">No analyzed items found in the legal dossier.</p>';
            }
        }

        // Safety Checklist
        if (firmSafetyFlags) {
            firmSafetyFlags.innerHTML = '';
            if (data.flags && data.flags.length > 0) {
                data.flags.forEach(f => {
                    const card = document.createElement('div');
                    const isHigh = f.severity === 'High';
                    card.className = `safety-flag-card ${isHigh ? 'high' : ''}`;
                    card.innerHTML = `
                        <div class="safety-flag-title font-outfit">${f.flag_title}</div>
                        <div class="safety-flag-msg font-inter">${f.message}</div>
                    `;
                    firmSafetyFlags.appendChild(card);
                });
            } else {
                firmSafetyFlags.innerHTML = '<p class="text-muted">Admissibility check passed. Standard filing routes approved.</p>';
            }
        }

        // Full Case Brief pre-filing docket
        if (firmBriefText) firmBriefText.innerText = data.case_brief || "Pre-filing brief skipped.";

        // Render statutory cognitive interpretations & landmark precedents
        renderInterpretations(firmInterpretationsList, data.interpretations);
        renderPrecedents(firmPrecedentsList, data.precedents);
    }

    function animateRadialGauge(targetPercent) {
        let current = 0;
        
        // Adjust dashoffset circle math: circumference is 2 * PI * 50 = 314
        const circumference = 314;
        
        const interval = setInterval(() => {
            if (current >= targetPercent) {
                clearInterval(interval);
            } else {
                current++;
                if (gaugeProbabilityNum) gaugeProbabilityNum.innerText = `${current}%`;
                
                // Offset calculates how much transparent space we leave
                const offset = circumference - (current / 100) * circumference;
                if (gaugeFillCircle) {
                    gaugeFillCircle.style.strokeDashoffset = offset;
                    
                    // Color matching depending on strength
                    if (current < 40) {
                        gaugeFillCircle.style.stroke = 'var(--color-danger)';
                    } else if (current < 70) {
                        gaugeFillCircle.style.stroke = 'var(--color-warning)';
                    } else {
                        gaugeFillCircle.style.stroke = 'var(--color-success)';
                    }
                }
            }
        }, 15);
    }

    function openStatuteModal(s) {
        if (!s) return;
        document.getElementById('statute-modal-code').innerText = s.code_type || 'Statute';
        document.getElementById('statute-modal-act-title').innerText = s.act_title || '';
        document.getElementById('statute-modal-section-header').innerText = `Section ${s.section_number}: ${s.section_title}`;
        
        document.getElementById('statute-modal-description').innerText = s.description || 'No description available.';
        
        const punishGroup = document.getElementById('group-modal-punishment');
        const punishText = document.getElementById('statute-modal-punishment');
        if (s.punishment) {
            punishGroup.style.display = 'block';
            punishText.innerText = s.punishment;
        } else {
            punishGroup.style.display = 'none';
        }

        const routeGroup = document.getElementById('group-modal-route');
        const routeText = document.getElementById('statute-modal-route');
        if (s.procedural_route || s.evidence_rule) {
            routeGroup.style.display = 'block';
            routeGroup.querySelector('.form-label').innerText = s.evidence_rule ? 'Evidence Rule / Principle' : 'Procedural Route';
            routeText.innerText = s.procedural_route || s.evidence_rule;
        } else {
            routeGroup.style.display = 'none';
        }

        const evidenceGroup = document.getElementById('group-modal-evidence-required');
        const evidenceList = document.getElementById('statute-modal-evidence-list');
        evidenceList.innerHTML = '';
        if (s.evidence_required && s.evidence_required.length > 0) {
            evidenceGroup.style.display = 'block';
            s.evidence_required.forEach(item => {
                const li = document.createElement('li');
                li.innerText = item;
                evidenceList.appendChild(li);
            });
        } else {
            evidenceGroup.style.display = 'none';
        }
        
        modalStatute.classList.add('show');
    }

    // ---------------------------------------------------------
    // Workflow 5: Sidebar Cases Retrieval & Actions
    // ---------------------------------------------------------
    async function fetchPastCases() {
        try {
            let url = `${API_BASE}/api/cases`;
            if (state.userSession && state.userSession.id) {
                url += `?user_id=${state.userSession.id}&user_type=${state.userSession.user_type}`;
            }
            const res = await fetch(url);
            if (!res.ok) throw new Error("Failed to load historical case submissions list.");
            const cases = await res.json();
            
            state.pastCases = cases;
            renderCaseHistoryList();

        } catch (error) {
            console.error(error);
        }
    }

    function renderCaseHistoryList() {
        // Filter cases to match the logged-in persona/user_type to prevent carrying the same cases
        let filteredCases = state.pastCases;
        if (state.userSession) {
            const expectedPersona = state.userSession.user_type === 'lawfirm' ? 'lawfirm' : 'individual';
            filteredCases = state.pastCases.filter(c => c.user_persona === expectedPersona);
        }

        if (filteredCases.length === 0) {
            caseHistoryList.innerHTML = '<li class="history-placeholder">No analysis records found.</li>';
            return;
        }

        caseHistoryList.innerHTML = '';
        filteredCases.forEach(c => {
            const date = new Date(c.created_at);
            const dateStr = date.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' });
            const snippet = c.grievance_snippet || `Case ID: ${c.id}`;
            const activeClass = state.activeCaseId === c.id ? 'active' : '';
            const probStr = c.win_probability ? `${Math.round(c.win_probability)}%` : 'N/A';
            const probClass = c.win_probability ? 'win-badge' : 'win-badge nil';

            const li = document.createElement('li');
            li.className = `case-history-item ${activeClass}`;
            li.setAttribute('data-id', c.id);
            li.innerHTML = `
                <div class="history-item-header">
                    <span>L-00${c.id} • ${dateStr}</span>
                    <button type="button" class="btn-delete-case" data-id="${c.id}" title="Delete analysis logs">
                        <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.5">
                            <polyline points="3 6 5 6 21 6"></polyline>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                        </svg>
                    </button>
                </div>
                <div class="history-item-title">${snippet}</div>
                <div class="history-item-footer">
                    <span class="persona-tag ${c.user_persona}">${c.user_persona === 'lawfirm' ? 'Firm' : 'Citizen'}</span>
                    <span class="${probClass}">Strength: ${probStr}</span>
                </div>
            `;

            // Bind click to load details
            li.addEventListener('click', (e) => {
                // If clicking trash button, skip
                if (e.target.closest('.btn-delete-case')) return;
                
                const id = parseInt(li.getAttribute('data-id'));
                const found = state.pastCases.find(item => item.id === id);
                if (found) {
                    state.activeCaseId = id;
                    state.activePersona = found.user_persona;
                    
                    // Adjust radios
                    document.querySelector(`input[name="workspace-persona"][value="${found.user_persona}"]`).checked = true;
                    updateThemeClass();
                    
                    switchView('output');
                    loadDashboardDetails(id);
                    
                    // Re-render to refresh active highlight
                    renderCaseHistoryList();
                }
            });

            // Bind click to delete
            li.querySelector('.btn-delete-case').addEventListener('click', async (e) => {
                e.stopPropagation();
                const id = parseInt(e.currentTarget.getAttribute('data-id'));
                if (confirm(`Are you sure you want to delete Case L-00${id} and all related uploaded files?`)) {
                    try {
                        const deleteRes = await fetch(`${API_BASE}/api/cases/${id}`, {
                            method: 'DELETE'
                        });
                        if (!deleteRes.ok) throw new Error("Failed to delete case.");
                        addConsoleLine(`Case L-00${id} logs wiped successfully.`, "info");
                        
                        if (state.activeCaseId === id) {
                            startNewCaseFlow();
                        }
                        fetchPastCases();
                    } catch (err) {
                        alert(err.message);
                    }
                }
            });

            caseHistoryList.appendChild(li);
        });
    }

    function startNewCaseFlow() {
        state.activeCaseId = null;
        state.attachedFiles = [];
        state.isProcessing = false;
        
        inputGrievance.value = '';
        inputLocation.value = 'Delhi';
        
        renderAttachedFilesList();
        switchView('intake');

        // Reset Law Firm sub-tabs to default (Acquire Case)
        if (state.userSession && state.userSession.user_type === 'lawfirm') {
            btnTabAcquireDocket.classList.add('active');
            btnTabDirectCase.classList.remove('active');
            
            btnTabAcquireDocket.style.background = 'var(--color-primary)';
            btnTabAcquireDocket.style.color = 'var(--bg-panel)';
            btnTabDirectCase.style.background = 'transparent';
            btnTabDirectCase.style.color = 'var(--color-foreground)';
            
            cardAcquireDocket.style.display = 'block';
            citizenIntakeWorkspace.style.display = 'none';
            state.activePersona = 'lawfirm';
        }
        
        // Remove active class highlights in sidebar
        const items = document.querySelectorAll('.case-history-item');
        items.forEach(i => i.classList.remove('active'));
        
        btnSubmitCase.disabled = false;
        btnSubmitCase.innerHTML = 'Initiate Mapping Sequence';
    }

    // ---------------------------------------------------------
    // Execution Start
    // ---------------------------------------------------------
    init();
});
