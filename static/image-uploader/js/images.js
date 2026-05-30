document.addEventListener('DOMContentLoaded', async () => {
    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') {
            window.location.href = '/upload';
        }
    });
    const fileListWrapper = document.getElementById('file-list-wrapper');
    const uploadRedirectButton = document.getElementById('upload-tab-btn');

    const updateTabStyles = () => {
        const uploadTab = document.getElementById('upload-tab-btn');
        const imagesTab = document.getElementById('images-tab-btn');

        const isImagesPage = window.location.pathname.includes('images');

        uploadTab.classList.remove('upload__tab--active');
        imagesTab.classList.remove('upload__tab--active');

        if (isImagesPage) {
            imagesTab.classList.add('upload__tab--active');
        } else {
            uploadTab.classList.add('upload__tab--active');
        }
    };

    function formatSize(bytes) {
        if (!bytes) return '-';
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }



    const displayFiles = async () => {
        fileListWrapper.innerHTML = '';

        const urlParams = new URLSearchParams(window.location.search);
        let page =  urlParams.get('page');
        if (page == null) {page = 1};
        if (Number(page) < 1) { window.location.href = `/images?page=1`; return;};
        const response = await fetch(`/api/images-data/?page=${page}`, { params: { page } }).then(res => res.json());
        const storedFiles = response.images;

        const prevButton = document.getElementById('prev-page-btn');
        const nextButton = document.getElementById('next-page-btn');

        prevButton.href = `/images?page=${Number(page) - 1}`;
        nextButton.href = `/images?page=${Number(page) + 1}`;

            if (Number(page) === 1) {
                prevButton.classList.add('disabled');
            } else {
                prevButton.classList.remove('disabled');
            }
            if (response.has_next ) {
                nextButton.classList.remove('disabled');
            } else {
                nextButton.classList.add('disabled');
            }


        const currentPage = document.getElementById('current-page');
        currentPage.textContent = page;




        if (storedFiles.length === 0) {
            if (Number(page) > 1) {
                    window.location.href = `/images?page=${Number(page) - 1}`;
                }
            fileListWrapper.innerHTML = '<p class="upload__promt" style="text-align: center; margin-top: 50px;">No images uploaded yet.</p>';
            const paginationWrapper = document.getElementById('pagination-wrapper');
            paginationWrapper.style.display = 'none';
        } else {
            const container = document.createElement('div');
            container.className = 'file-list-container';
            const header = document.createElement('div');
            header.className = 'file-list-header';
            header.innerHTML = `
                <div class="file-col file-col-image">Image</div>
                <div class="file-col file-col-name">Name</div>
                <div class="file-col file-col-date">Date</div>
                <div class="file-col file-col-size">Size</div>
                <div class="file-col file-col-url">Url</div>
                <div class="file-col file-col-delete">Delete</div>
            `;
            container.appendChild(header);

            const list = document.createElement('div');
            list.id = 'file-list';

            storedFiles.forEach((image) => {
                const imageUrl = `${window.location.origin}/images/${image.filename}.${image.file_type}`;
                const fileItem = document.createElement('div');
                fileItem.className = 'file-list-item';
                fileItem.innerHTML = `
                    <div class="file-col file-col-image">
                        <img src="${imageUrl}" alt="file icon" width="20%">
                    </div>
                    <div class="file-col file-col-name">
                        <span class="file-name">${image.original_name}</span>
                    </div>
                    <div class="file-col file-col-date">
                        ${image.upload_time ? `${image.upload_time}` : '—'}
                    </div>
                    <div class="file-col file-col-size">
                        ${formatSize(image.size)}
                    </div>
                    <div class="file-col file-col-url">
                        <a href="${imageUrl}" target="_blank">${imageUrl}</a>
                    </div>
                    <div class="file-col file-col-delete">
                        <button data-filename="${image.filename}.${image.file_type}" class="delete-btn">
                            <img src="/static/image-uploader/img/icon/delete.png" alt="delete icon">
                        </button>
                    </div>
                `;


                list.appendChild(fileItem);
            });

            container.appendChild(list);
            fileListWrapper.appendChild(container);
            addDeleteListeners();
        }

        updateTabStyles();
    };

    const addDeleteListeners = async () => {
        document.querySelectorAll('.delete-btn').forEach((button) => {
            button.addEventListener('click', async (event) => {
                const filename = event.currentTarget.dataset.filename;
                try {
                     await fetch(`/api/images/${filename}`, {
                        method: 'DELETE'
                     });

                     await displayFiles();
                } catch (e) {
                    console.log('File deletion failed');
                }
            });
        });
    };

    if (uploadRedirectButton) {
        uploadRedirectButton.addEventListener('click', () => {
            window.location.href = '/upload';
        });
    }

    displayFiles();
});