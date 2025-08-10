document.addEventListener('DOMContentLoaded', () => {
    const mainContent = document.getElementById('main-content');
    const sidebar = document.getElementById('josephus-sidebar');
    const josephusContent = document.getElementById('josephus-content');
    const closeSidebarBtn = document.getElementById('close-sidebar');
    const lukeTextContainer = document.getElementById('luke-text-container');
    
    let parallelsData = {};

    // --- MAIN FUNCTION ---
    async function initialize() {
        try {
            // Fetch both the processed JSON and the Luke text
            const [parallels, lukeText] = await Promise.all([
                fetch('full_parallels.json').then(res => res.json()),
                fetch('luke.txt').then(res => res.text())
            ]);
            
            parallelsData = parallels;
            displayLuke(lukeText);
            setupEventListeners();

        } catch (error) {
            console.error("Error loading data:", error);
            lukeTextContainer.innerHTML = "<p>Error loading data files. Please ensure 'luke.txt' and 'full_parallels.json' are available.</p>";
        }
    }

    // --- RENDER AND EVENT FUNCTIONS ---
    function displayLuke(text) {
        const verses = text.split(/\n\s*\n/);
        let currentChapter = -1;
        let chapterDiv;

        verses.forEach(block => {
            const match = block.match(/Luke (\d+):(\d+):\s*([\s\S]+)/);
            if (!match) return;

            const chapter = match[1];
            const verse = match[2];
            const verseText = match[3].trim();
            
            if (parseInt(chapter) !== currentChapter) {
                currentChapter = parseInt(chapter);
                chapterDiv = document.createElement('div');
                chapterDiv.innerHTML = `<h2 class="chapter-title">Chapter ${chapter}</h2>`;
                lukeTextContainer.appendChild(chapterDiv);
            }

            const verseSpan = document.createElement('span');
            // Check if parallels exist for this chapter and verse
            if (parallelsData[chapter] && parallelsData[chapter][verse]) {
                verseSpan.className = 'verse parallel';
                verseSpan.dataset.lukeRef = `${chapter}:${verse}`;
            } else {
                verseSpan.className = 'verse';
            }
            
            verseSpan.innerHTML = `<sup class="verse-number">${verse}</sup> ${verseText} `;
            chapterDiv.appendChild(verseSpan);
        });
    }

    function setupEventListeners() {
        // Event listener for clicking on a highlighted Luke verse
        lukeTextContainer.addEventListener('click', (event) => {
            const target = event.target.closest('.parallel');
            if (!target) return;

            const lukeRef = target.dataset.lukeRef;
            const [chapter, verse] = lukeRef.split(':');
            const parallelEntries = parallelsData[chapter][verse];

            if (parallelEntries) {
                josephusContent.innerHTML = ''; // Clear previous content
                parallelEntries.forEach(entry => {
                    const entryDiv = document.createElement('div');
                    entryDiv.className = 'parallel-entry';
                    entryDiv.innerHTML = `<h4>${entry.ref}</h4><p>${entry.text}</p>`;
                    josephusContent.appendChild(entryDiv);
                });
                showSidebar();
            }
        });

        // Event listener for the close button
        closeSidebarBtn.addEventListener('click', hideSidebar);
    }

    function showSidebar() {
        sidebar.classList.add('visible');
        mainContent.classList.add('sidebar-visible');
    }

    function hideSidebar() {
        sidebar.classList.remove('visible');
        mainContent.classList.remove('sidebar-visible');
    }

    // Start the application
    initialize();
});