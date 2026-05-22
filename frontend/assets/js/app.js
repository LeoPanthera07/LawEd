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
        apiSettings: {
            provider: 'simulation',
            apiKey: ''
        }
    };

    const API_BASE = window.location.origin;

    // ---------------------------------------------------------
    // DOM Elements Cache
    // ---------------------------------------------------------
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

    // Intake Form & Uploads
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

    // Settings Modal
    const modalSettings = document.getElementById('modal-settings');
    const formBYOKSettings = document.getElementById('form-byok-settings');
    const byokProvider = document.getElementById('byok-provider');
    const groupApiKey = document.getElementById('group-api-key');
    const byokKey = document.getElementById('byok-key');
    const btnSettingsClose = document.getElementById('btn-settings-close');
    const btnSettingsCancel = document.getElementById('btn-settings-cancel');

    // ---------------------------------------------------------
    // App Initialization
    // ---------------------------------------------------------
    function init() {
        loadSettingsFromLocalStorage();
        updateThemeClass();
        switchView('intake');
        fetchPastCases();
        setupEventListeners();
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

            const res = await fetch(`${API_BASE}/api/cases`, {
                method: "POST",
                body: caseData
            });

            if (!res.ok) throw new Error("Failed to register case submission.");
            const caseResult = await res.json();
            const caseId = caseResult.case_id;
            state.activeCaseId = caseId;
            
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
            // Trigger asynchronous agent analysis API route
            // Since this runs in a couple of seconds synchronously on mock/fast completions,
            // we will simulate the pulsing visual steps with slight intervals or bind directly to the JSON response
            
            // Update Active Indicators sequentially to make it feel premium, pulsing, and active!
            await animateAgentSequence();

            const res = await fetch(`${API_BASE}/api/cases/${caseId}/analyze`, {
                method: "POST",
                headers: headers
            });

            if (!res.ok) throw new Error("Agentic orchestrator encountered an error.");
            const results = await res.json();
            
            addConsoleLine("Multi-agent analysis complete. Structuring outcomes.", "success");
            
            // Step D: Direct next navigation
            setTimeout(() => {
                state.isProcessing = false;
                btnSubmitCase.disabled = false;
                btnSubmitCase.innerHTML = 'Initiate Mapping Sequence';
                
                if (state.activePersona === 'lawfirm') {
                    // Transition to simulated courtroom arena
                    switchView('courtroom');
                    loadCourtroomObjections(caseId);
                } else {
                    // Transition straight to Output Brief
                    switchView('output');
                    loadDashboardDetails(caseId);
                }
                
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
        consoleLogs.innerHTML = '';
        const rows = [rowAgentIntake, rowAgentEvidence, rowAgentLegal, rowAgentReview, rowAgentDrafting, rowAgentPlaintiff, rowAgentDefense, rowAgentJudge];
        const statuses = [statusAgentIntake, statusAgentEvidence, statusAgentLegal, statusAgentReview, statusAgentDrafting, statusAgentPlaintiff, statusAgentDefense, statusAgentJudge];
        
        rows.forEach(r => r.classList.remove('active', 'completed'));
        statuses.forEach(s => s.innerText = "Waiting in pool...");
    }

    async function animateAgentSequence() {
        const delay = (ms) => new Promise(res => setTimeout(res, ms));
        
        // Intake
        rowAgentIntake.classList.add('active');
        statusAgentIntake.innerText = "Processing grievance facts...";
        addConsoleLine("> Intake Fact Extractor: Parsing sentence semantic frames...", "info");
        await delay(1200);
        rowAgentIntake.classList.remove('active');
        rowAgentIntake.classList.add('completed');
        statusAgentIntake.innerText = "Facts extracted successfully.";
        addConsoleLine("> Intake Fact Extractor: Facts database records created.", "success");

        // Evidence
        rowAgentEvidence.classList.add('active');
        statusAgentEvidence.innerText = "Scanning attachments for credibility...";
        addConsoleLine("> Evidence Verifier: Running simulated OCR text extraction...", "info");
        await delay(1000);
        rowAgentEvidence.classList.remove('active');
        rowAgentEvidence.classList.add('completed');
        statusAgentEvidence.innerText = "Evidence credibility rated.";
        addConsoleLine("> Evidence Verifier: Digital files assigned support ratings.", "success");

        // Legal (RAG)
        rowAgentLegal.classList.add('active');
        statusAgentLegal.innerText = "Matching sections in BNS, BSA, BNSS...";
        addConsoleLine("> Statutory RAG Matcher: Querying corpus index files...", "info");
        await delay(1300);
        rowAgentLegal.classList.remove('active');
        rowAgentLegal.classList.add('completed');
        statusAgentLegal.innerText = "Statutes mapped successfully.";
        addConsoleLine("> Statutory RAG Matcher: Sections BNS 318, BSA 63, BNSS 173 bound.", "success");

        // Review
        rowAgentReview.classList.add('active');
        statusAgentReview.innerText = "Analyzing litigation risks and gaps...";
        addConsoleLine("> Integrity Reviewer: Verifying digital certificates requirements under Section 63 BSA...", "info");
        await delay(1100);
        rowAgentReview.classList.remove('active');
        rowAgentReview.classList.add('completed');
        statusAgentReview.innerText = "Integrity checked. Risks flagged.";
        addConsoleLine("> Integrity Reviewer: Safety alerts compiled.", "success");

        // Drafting
        rowAgentDrafting.classList.add('active');
        statusAgentDrafting.innerText = "Building pre-filing Case Brief...";
        addConsoleLine("> Case Brief Drafter: Formulating legal brief structure...", "info");
        await delay(1000);
        rowAgentDrafting.classList.remove('active');
        rowAgentDrafting.classList.add('completed');
        statusAgentDrafting.innerText = "Case Brief draft constructed.";
        addConsoleLine("> Case Brief Drafter: Completed Case Preparation Package.", "success");

        if (state.activePersona === 'lawfirm') {
            // Plaintiff
            rowAgentPlaintiff.classList.add('active');
            statusAgentPlaintiff.innerText = "Structuring Prosecution opening arguments...";
            addConsoleLine("> Complainant Opening Counsel: Citing BNS and mapping facts to elements...", "info");
            await delay(1000);
            rowAgentPlaintiff.classList.remove('active');
            rowAgentPlaintiff.classList.add('completed');
            statusAgentPlaintiff.innerText = "Aggressive Opening compiled.";
            addConsoleLine("> Complainant Opening Counsel: Opened litigation.", "success");

            // Defense
            rowAgentDefense.classList.add('active');
            statusAgentDefense.innerText = "Formulating defense hurdles & objections...";
            addConsoleLine("> Defense Objection Counsel: Searching admissibility issues under BSA Section 63...", "info");
            await delay(1200);
            rowAgentDefense.classList.remove('active');
            rowAgentDefense.classList.add('completed');
            statusAgentDefense.innerText = "Adversarial challenges prepared.";
            addConsoleLine("> Defense Objection Counsel: Lodged digital evidence objection.", "success");

            // Judge
            rowAgentJudge.classList.add('active');
            statusAgentJudge.innerText = "Summoning verdict and probability rates...";
            addConsoleLine("> Judicial Adjudicator: Weighting arguments. Summing evidence rates...", "info");
            await delay(1000);
            rowAgentJudge.classList.remove('active');
            rowAgentJudge.classList.add('completed');
            statusAgentJudge.innerText = "Hon'ble Magistrate verdict filed.";
            addConsoleLine("> Judicial Adjudicator: Case evaluation finished.", "success");
        }
    }

    function addConsoleLine(text, type = "") {
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
            }

        } catch (error) {
            console.error(error);
            alert("Error loading case dashboard results: " + error.message);
        }
    }

    function renderIndividualDashboard(data) {
        // Parties
        indPartyComplainant.innerText = data.parties?.complainant || "User (Informant)";
        indPartyAccused.innerText = data.parties?.accused || "Accused Suspect";

        // Facts
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

        // Timeline
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

        // Draft case Brief
        indBriefText.innerText = data.case_brief || "Case brief draft construction was skipped.";

        // Statutes
        indStatuteStack.innerHTML = '';
        if (data.statutes && data.statutes.length > 0) {
            data.statutes.forEach(s => {
                const card = document.createElement('div');
                card.className = 'statute-pill-card';
                card.innerHTML = `
                    <div class="statute-pill-header">
                        <span class="statute-pill-num text-accent">Sec ${s.section_number}</span>
                        <span class="statute-pill-act">${s.code_type}</span>
                    </div>
                    <div class="statute-pill-title font-outfit">${s.section_title}</div>
                    <div class="statute-pill-desc">${s.description || ""}</div>
                    ${s.punishment ? `<div class="statute-pill-punish"><strong class="text-accent">Punishment:</strong> ${s.punishment}</div>` : ''}
                    ${s.procedural_route ? `<div class="statute-pill-route"><strong>Filing Route:</strong> ${s.procedural_route}</div>` : ''}
                `;
                indStatuteStack.appendChild(card);
            });
        } else {
            indStatuteStack.innerHTML = '<p class="text-muted">No specific penal code matches found.</p>';
        }

        // Evidence Audit
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

        // Safety Flags
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

    function renderLawfirmDashboard(data) {
        // 1. Radial gauge animation
        const prob = Math.round(data.win_probability || 50);
        animateRadialGauge(prob);

        // Timeline & Dossier
        firmPartyComplainant.innerText = data.parties?.complainant || "Prosecution";
        firmPartyAccused.innerText = data.parties?.accused || "Accused";

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

        // Statutes
        firmStatuteStack.innerHTML = '';
        if (data.statutes && data.statutes.length > 0) {
            data.statutes.forEach(s => {
                const card = document.createElement('div');
                card.className = 'statute-pill-card';
                card.innerHTML = `
                    <div class="statute-pill-header">
                        <span class="statute-pill-num text-accent">Sec ${s.section_number}</span>
                        <span class="statute-pill-act">${s.code_type}</span>
                    </div>
                    <div class="statute-pill-title font-outfit">${s.section_title}</div>
                    ${s.procedural_route ? `<div class="statute-pill-route" style="border:none;margin:0;padding:0;"><strong>Authority:</strong> ${s.procedural_route}</div>` : ''}
                `;
                firmStatuteStack.appendChild(card);
            });
        } else {
            firmStatuteStack.innerHTML = '<p class="text-muted">No matched statutes compiled.</p>';
        }

        // Strategy Report
        firmStrategyBrief.innerText = data.strategy_report || "Litigation opponent strategy report skipped.";

        // Verdict Order
        firmVerdictText.innerText = data.judge_verdict || "Magistrate verdict skipped.";

        // Evidence Audit
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

        // Safety Checklist
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

        // Full Case Brief pre-filing docket
        firmBriefText.innerText = data.case_brief || "Pre-filing brief skipped.";
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
                gaugeProbabilityNum.innerText = `${current}%`;
                
                // Offset calculates how much transparent space we leave
                const offset = circumference - (current / 100) * circumference;
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
        }, 15);
    }

    // ---------------------------------------------------------
    // Workflow 5: Sidebar Cases Retrieval & Actions
    // ---------------------------------------------------------
    async function fetchPastCases() {
        try {
            const res = await fetch(`${API_BASE}/api/cases`);
            if (!res.ok) throw new Error("Failed to load historical case submissions list.");
            const cases = await res.json();
            
            state.pastCases = cases;
            renderCaseHistoryList();

        } catch (error) {
            console.error(error);
        }
    }

    function renderCaseHistoryList() {
        if (state.pastCases.length === 0) {
            caseHistoryList.innerHTML = '<li class="history-placeholder">No analysis records found.</li>';
            return;
        }

        caseHistoryList.innerHTML = '';
        state.pastCases.forEach(c => {
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
                        } else {
                            fetchPastCases();
                        }
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
