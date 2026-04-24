    async function unlockBookRequest(bookId) {
        const token = localStorage.getItem('token');
        requestPageBtn.innerText = '...';
        requestPageBtn.disabled = true;
        
        try {
            const res = await fetch(`${API_URL}/books/${bookId}/unlock`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                userLibrary.push(bookId);
                showToast(t('unlockSuccess'));
                showDeliveryOptions();
            } else {
                const data = await res.json();
                alert(data.detail || 'Error unlocking book.');
            }
        } catch(e) {
            console.error(e);
        } finally {
            requestPageBtn.disabled = false;
        }
    }