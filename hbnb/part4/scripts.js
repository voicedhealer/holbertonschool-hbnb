document.addEventListener('DOMContentLoaded', () => {
    // -----------------------------------------
    // OUTIL : lire un cookie par son nom
    // -----------------------------------------
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    // Récupération du JWT une seule fois au début
    const jwt = getCookie('jwt');

    // -----------------------------------------
    // Gestion bouton Connexion / Déconnexion
    // -----------------------------------------
    const loginBtn = document.querySelector('.login-button');
    if (loginBtn) {
        const newLoginBtn = loginBtn.cloneNode(true);
        loginBtn.parentNode.replaceChild(newLoginBtn, loginBtn);

        if (jwt) {
            newLoginBtn.textContent = "Déconnexion";
            newLoginBtn.href = "#";
            newLoginBtn.addEventListener('click', (e) => {
                e.preventDefault();
                // Supprime cookie JWT (expire dans le passé)
                document.cookie = "jwt=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC; SameSite=Lax";
                window.location.replace('index.html');
            });
        } else {
            newLoginBtn.textContent = "Connexion";
            newLoginBtn.href = "login.html";
        }
    }

    // -----------------------------------------
    // PAGE LOGIN : gestion formulaire connexion + erreurs
    // -----------------------------------------
    const loginForm = document.getElementById('login-form');
    const loginError = document.getElementById('login-error');
    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value;
            const payload = { email, password };

            try {
                const response = await fetch('http://localhost:5001/api/v1/auth/login', {
                    method: 'POST',
                    credentials: 'include',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (response.ok) {
                    const data = await response.json();
                    if (data.access_token) {
                        // Stockage cookie JWT
                        document.cookie = `jwt=${data.access_token}; path=/; SameSite=Lax`;
                        // Redirection vers la page d'accueil
                        window.location.replace('index.html');
                    } else {
                        throw new Error("Le serveur n'a pas retourné de token.");
                    }
                } else {
                    let msg = 'Identifiants invalides';
                    try {
                        const err = await response.json();
                        if (err.message) msg = err.message;
                    } catch (_) { }
                    throw new Error(msg);
                }
            } catch (error) {
                if (loginError) {
                    loginError.textContent = error.message || "Erreur de connexion";
                    loginError.style.display = 'block';
                } else {
                    alert(error.message || "Erreur de connexion");
                }
            }
        });
    }

    // -----------------------------------------
    // PAGE ACCUEIL (index.html) : affichage lieux + filtrage par prix
    // -----------------------------------------
    const placesList = document.getElementById('places-list');
    const priceFilter = document.getElementById('price-filter');
    if (placesList && priceFilter) {
        const options = jwt ? { 
            headers: { 'Authorization': 'Bearer ' + jwt },
            credentials: 'include'
        } : {};

        fetch('http://localhost:5001/api/v1/places/', options)
            .then(resp => {
                if (!resp.ok) throw new Error(`Erreur API (${resp.status}): ${resp.statusText}`);
                return resp.json();
            })
            .then(places => {
                placesList.innerHTML = '';

                places.forEach(place => {
                    const card = document.createElement('div');
                    card.className = 'place-card';
                    card.dataset.price = place.price_by_night;
                    card.innerHTML = `
                        <h3 class="place-name">${place.name}</h3>
                        <p class="place-price">${place.price_by_night} €/nuit</p>
                        <button class="details-button" onclick="window.location.href='place.html?id=${place.id}'">
                          Voir les détails
                        </button>
                    `;
                    placesList.appendChild(card);
                });

                // Génération options filtres prix (prix uniques triés)
                const uniqPrices = Array.from(new Set(places.map(p => p.price_by_night))).sort((a, b) => a - b);
                priceFilter.innerHTML = `<option value="">Tous</option>` +
                    uniqPrices.map(prix => `<option value="${prix}">≤ ${prix} €</option>`).join('');

                // Événement filtrage des lieux par prix via style.display
                priceFilter.addEventListener('change', () => {
                    const max = Number(priceFilter.value);
                    const cards = placesList.querySelectorAll('.place-card');
                    let nbVisible = 0;

                    cards.forEach(card => {
                        const price = Number(card.dataset.price);
                        const visible = !max || price <= max;
                        card.style.display = visible ? '' : 'none';
                        if (visible) nbVisible++;
                    });

                    // Gestion du message "Aucun lieu"
                    let msg = document.getElementById('msg-vide');
                    if (nbVisible === 0) {
                        if (!msg) {
                            msg = document.createElement('p');
                            msg.id = 'msg-vide';
                            msg.textContent = "Aucun lieu ne correspond à ce critère.";
                            msg.style.color = "gray";
                            placesList.appendChild(msg);
                        }
                    } else if (msg) {
                        msg.remove();
                    }
                });
            })
            .catch(err => {
                placesList.innerHTML = `<p>Erreur lors du chargement des lieux : ${err.message}</p>`;
                console.error(err);
            });
    }

    // -----------------------------------------
    // ✅ PAGE CREATE PLACE - Formulaire de création avec validation AMÉLIORÉ
    // -----------------------------------------
    const createPlaceForm = document.getElementById('create-place-form');
    const createPlaceError = document.getElementById('create-place-error');
    const createPlaceSuccess = document.getElementById('create-place-success');

    if (createPlaceForm) {
        // Vérification que l'utilisateur est connecté
        if (!jwt) {
            document.body.innerHTML = `
                <div style="text-align: center; margin-top: 50px;">
                    <h2>Accès refusé</h2>
                    <p>Vous devez être connecté pour créer un lieu.</p>
                    <a href="login.html" style="color: #007bff;">Se connecter</a>
                </div>
            `;
            return;
        }

        // ✅ FONCTION LOADAMENITIES COMPLÈTEMENT REÉCRITE ET SÉCURISÉE
        function loadAmenities() {
            const amenitiesContainer = document.getElementById('amenities-container');
            if (!amenitiesContainer) {
                console.error('Container amenities-container introuvable');
                return;
            }

            // Éviter les chargements multiples
            if (amenitiesContainer.dataset.loading === 'true') {
                console.log('Amenities déjà en cours de chargement...');
                return;
            }

            if (amenitiesContainer.dataset.loaded === 'true') {
                console.log('Amenities déjà chargées');
                return;
            }

            // Marquer comme en cours de chargement
            amenitiesContainer.dataset.loading = 'true';
            amenitiesContainer.innerHTML = '<div class="loading-amenities"><p>🔄 Chargement des équipements...</p></div>';

            console.log('🚀 Début du chargement des amenities...');

            fetch('http://localhost:5001/api/v1/amenities/', {
                headers: { 'Authorization': 'Bearer ' + jwt },
                credentials: 'include'
            })
            .then(resp => {
                console.log('📡 Réponse API amenities:', resp.status);
                if (!resp.ok) {
                    throw new Error(`Erreur API: ${resp.status} ${resp.statusText}`);
                }
                return resp.json();
            })
            .then(amenities => {
                console.log('📦 Amenities reçues:', amenities);
                console.log('📊 Nombre d\'amenities:', amenities?.length || 0);

                // Vider le container
                amenitiesContainer.innerHTML = '';

                // Vérifier que amenities est un tableau
                if (!Array.isArray(amenities)) {
                    throw new Error('Format de données invalide: amenities n\'est pas un tableau');
                }

                if (amenities.length === 0) {
                    amenitiesContainer.innerHTML = '<p style="color: #6c757d; text-align: center;">Aucun équipement disponible</p>';
                    return;
                }

                // ✅ ÉLIMINATION DES DOUBLONS côté client
                const uniqueAmenities = amenities.filter((amenity, index, self) => {
                    // Garder seulement le premier élément de chaque ID unique
                    return index === self.findIndex(a => a.id === amenity.id);
                });

                console.log('🔧 Amenities uniques après filtrage:', uniqueAmenities.length);

                // Créer les checkboxes pour chaque amenity unique
                uniqueAmenities.forEach((amenity, index) => {
                    console.log(`➕ Création checkbox ${index + 1}:`, amenity.name);
                    
                    const checkboxDiv = document.createElement('div');
                    checkboxDiv.className = 'amenity-checkbox';
                    checkboxDiv.innerHTML = `
                        <label>
                            <input type="checkbox" name="amenities" value="${amenity.id}">
                            ${amenity.name}
                        </label>
                    `;
                    amenitiesContainer.appendChild(checkboxDiv);
                });

                // Marquer comme chargé avec succès
                amenitiesContainer.dataset.loaded = 'true';
                amenitiesContainer.dataset.loading = 'false';
                console.log('✅ Amenities chargées avec succès!');
            })
            .catch(err => {
                console.error('❌ Erreur chargement amenities:', err);
                amenitiesContainer.innerHTML = `
                    <div style="color: #dc3545; text-align: center; padding: 20px;">
                        <p>❌ Erreur de chargement des équipements</p>
                        <p style="font-size: 12px;">${err.message}</p>
                        <button onclick="location.reload()" style="background: #007bff; color: white; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer;">
                            Recharger la page
                        </button>
                    </div>
                `;
                amenitiesContainer.dataset.loading = 'false';
            });
        }

        // Charger les amenities au chargement de la page
        loadAmenities();

        // ✅ FONCTIONS UTILITAIRES POUR VALIDATION (déclarées EN PREMIER)
        function showFieldError(errorId, message) {
            const errorSpan = document.getElementById(errorId);
            if (errorSpan) {
                errorSpan.textContent = message;
                errorSpan.style.display = 'block';
            }
        }

        function hideFieldError(errorId) {
            const errorSpan = document.getElementById(errorId);
            if (errorSpan) {
                errorSpan.style.display = 'none';
            }
        }

        // ✅ FONCTIONS DE VALIDATION GPS (déclarées correctement)
        function validateLatitude(latitudeInput) {
            const value = parseFloat(latitudeInput.value);
            if (!latitudeInput.value.trim()) {
                showFieldError('latitude-error', 'La latitude est obligatoire');
                latitudeInput.classList.add('error');
                return false;
            } else if (isNaN(value) || value < -90 || value > 90) {
                showFieldError('latitude-error', 'La latitude doit être entre -90 et 90');
                latitudeInput.classList.add('error');
                return false;
            } else {
                hideFieldError('latitude-error');
                latitudeInput.classList.remove('error');
                return true;
            }
        }

        function clearLatitudeError(latitudeInput) {
            if (latitudeInput.classList.contains('error')) {
                hideFieldError('latitude-error');
                latitudeInput.classList.remove('error');
            }
        }

        function validateLongitude(longitudeInput) {
            const value = parseFloat(longitudeInput.value);
            if (!longitudeInput.value.trim()) {
                showFieldError('longitude-error', 'La longitude est obligatoire');
                longitudeInput.classList.add('error');
                return false;
            } else if (isNaN(value) || value < -180 || value > 180) {
                showFieldError('longitude-error', 'La longitude doit être entre -180 et 180');
                longitudeInput.classList.add('error');
                return false;
            } else {
                hideFieldError('longitude-error');
                longitudeInput.classList.remove('error');
                return true;
            }
        }

        function clearLongitudeError(longitudeInput) {
            if (longitudeInput.classList.contains('error')) {
                hideFieldError('longitude-error');
                longitudeInput.classList.remove('error');
            }
        }

        // ✅ VALIDATION EN TEMPS RÉEL DES CHAMPS (corrigée)
        const titleInput = document.getElementById('place-title');
        const descriptionInput = document.getElementById('place-description');
        const priceInput = document.getElementById('place-price');
        const latitudeInput = document.getElementById('place-latitude');
        const longitudeInput = document.getElementById('place-longitude');

        // Validation du titre (obligatoire, min 3 caractères)
        if (titleInput) {
            titleInput.addEventListener('input', () => {
                hideFieldError('title-error');
                titleInput.classList.remove('error');
            });

            titleInput.addEventListener('blur', () => {
                const value = titleInput.value.trim();
                if (!value) {
                    showFieldError('title-error', 'Le titre est obligatoire');
                    titleInput.classList.add('error');
                } else if (value.length < 3) {
                    showFieldError('title-error', 'Le titre doit contenir au moins 3 caractères');
                    titleInput.classList.add('error');
                } else {
                    hideFieldError('title-error');
                    titleInput.classList.remove('error');
                }
            });
        }

        // Validation du prix (obligatoire, positif)
        if (priceInput) {
            priceInput.addEventListener('input', () => {
                hideFieldError('price-error');
                priceInput.classList.remove('error');
            });

            priceInput.addEventListener('blur', () => {
                const value = parseFloat(priceInput.value);
                if (!priceInput.value) {
                    showFieldError('price-error', 'Le prix est obligatoire');
                    priceInput.classList.add('error');
                } else if (isNaN(value) || value <= 0) {
                    showFieldError('price-error', 'Le prix doit être un nombre positif');
                    priceInput.classList.add('error');
                } else {
                    hideFieldError('price-error');
                    priceInput.classList.remove('error');
                }
            });
        }

        // Validation latitude (corrigée)
        if (latitudeInput) {
            latitudeInput.addEventListener('input', () => clearLatitudeError(latitudeInput));
            latitudeInput.addEventListener('focus', () => clearLatitudeError(latitudeInput));
            latitudeInput.addEventListener('blur', () => validateLatitude(latitudeInput));
        }

        // Validation longitude (corrigée)
        if (longitudeInput) {
            longitudeInput.addEventListener('input', () => clearLongitudeError(longitudeInput));
            longitudeInput.addEventListener('focus', () => clearLongitudeError(longitudeInput));
            longitudeInput.addEventListener('blur', () => validateLongitude(longitudeInput));
        }

        // ✅ SOUMISSION DU FORMULAIRE (améliorée)
        createPlaceForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            
            // Masquer les messages précédents
            if (createPlaceError) createPlaceError.style.display = 'none';
            if (createPlaceSuccess) createPlaceSuccess.style.display = 'none';

            // Collecte des données du formulaire
            const formData = new FormData(createPlaceForm);
            const selectedAmenities = Array.from(document.querySelectorAll('input[name="amenities"]:checked'))
                .map(checkbox => checkbox.value);

            const placeData = {
                title: formData.get('title')?.trim() || '',
                description: formData.get('description')?.trim() || '',
                price: parseFloat(formData.get('price') || '0'),
                latitude: parseFloat(formData.get('latitude') || '0'),
                longitude: parseFloat(formData.get('longitude') || '0'),
                owner_id: "auto", // Sera défini côté serveur via JWT
                amenities: selectedAmenities
            };

            console.log('📋 Données à envoyer:', placeData);

            // Validation finale côté client
            const validationErrors = [];
            
            if (!placeData.title || placeData.title.length < 3) {
                validationErrors.push('Le titre doit contenir au moins 3 caractères');
            }
            
            if (!placeData.price || placeData.price <= 0) {
                validationErrors.push('Le prix doit être un nombre positif');
            }
            
            if (isNaN(placeData.latitude) || placeData.latitude < -90 || placeData.latitude > 90) {
                validationErrors.push('Latitude invalide (doit être entre -90 et 90)');
            }
            
            if (isNaN(placeData.longitude) || placeData.longitude < -180 || placeData.longitude > 180) {
                validationErrors.push('Longitude invalide (doit être entre -180 et 180)');
            }

            if (validationErrors.length > 0) {
                if (createPlaceError) {
                    createPlaceError.innerHTML = validationErrors.join('<br>');
                    createPlaceError.style.display = 'block';
                }
                return;
            }

            try {
                // Désactiver le bouton pendant l'envoi
                const submitButton = createPlaceForm.querySelector('button[type="submit"]');
                const originalText = submitButton?.textContent || 'Créer le lieu';
                if (submitButton) {
                    submitButton.disabled = true;
                    submitButton.textContent = 'Création en cours...';
                }

                console.log('🚀 Envoi des données au serveur...');

                const response = await fetch('http://localhost:5001/api/v1/places/', {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + jwt
                    },
                    body: JSON.stringify(placeData)
                });

                console.log('📡 Réponse serveur:', response.status);

                if (response.ok) {
                    const newPlace = await response.json();
                    console.log('✅ Lieu créé:', newPlace);
                    
                    // Afficher le message de succès
                    if (createPlaceSuccess) {
                        createPlaceSuccess.innerHTML = `
                            <strong>Succès !</strong> Votre lieu "${newPlace.name}" a été créé avec succès.
                            <br><a href="place.html?id=${newPlace.id}">Voir le lieu créé</a>
                        `;
                        createPlaceSuccess.style.display = 'block';
                    }
                    
                    // Réinitialiser le formulaire
                    createPlaceForm.reset();
                    
                    // Redirection automatique après 3 secondes
                    setTimeout(() => {
                        window.location.href = `place.html?id=${newPlace.id}`;
                    }, 3000);
                    
                } else {
                    let errorMessage = 'Erreur lors de la création du lieu';
                    try {
                        const errorData = await response.json();
                        console.log('❌ Erreur serveur:', errorData);
                        if (errorData.error) {
                            errorMessage = errorData.error;
                        } else if (errorData.message) {
                            errorMessage = errorData.message;
                        }
                    } catch (_) {}
                    
                    throw new Error(errorMessage);
                }
            } catch (error) {
                console.error('❌ Erreur création lieu:', error);
                if (createPlaceError) {
                    createPlaceError.textContent = error.message || 'Erreur inconnue lors de la création';
                    createPlaceError.style.display = 'block';
                }
            } finally {
                // Réactiver le bouton
                const submitButton = createPlaceForm.querySelector('button[type="submit"]');
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.textContent = originalText;
                }
            }
        });
    }

    // -----------------------------------------
    // PAGE DETAILS (place.html) : infos lieu, avis, formulaire avis
    // -----------------------------------------
    const placeDetailsSection = document.querySelector('.place-details');
    if (placeDetailsSection) {
        // Extraction place_id depuis URL
        function getPlaceIdFromUrl() {
            const params = new URLSearchParams(window.location.search);
            return params.get('id');
        }
        
        const placeId = getPlaceIdFromUrl();
        if (!placeId) {
            const placeInfo = document.querySelector('.place-info');
            if (placeInfo) placeInfo.innerHTML = "<p>Lieu inconnu</p>";
            return;
        }

        // Charge infos lieu + avis
        function fetchPlaceAndReviews() {
            const fetchOptions = jwt ? { 
                headers: { 'Authorization': 'Bearer ' + jwt },
                credentials: 'include'
            } : {};

            // Infos lieu
            fetch(`http://localhost:5001/api/v1/places/${placeId}`, fetchOptions)
                .then(resp => {
                    if (!resp.ok) throw new Error("Lieu introuvable");
                    return resp.json();
                })
                .then(place => {
                    const infoDiv = document.querySelector('.place-info');
                    if (infoDiv) {
                        infoDiv.innerHTML = `
                            <h1>${place.name} (${place.city_name || ""})</h1>
                            <p>Hébergé par <span class="host">${place.host_name || "Inconnu"}</span></p>
                            <p class="place-price">Prix : ${place.price_by_night} €/nuit</p>
                            <p>Description : ${place.description || ''}</p>
                            <ul>
                                ${(place.amenities || []).map(am => `<li>${am.name}</li>`).join('')}
                            </ul>
                        `;
                    }
                })
                .catch(err => {
                    const infoDiv = document.querySelector('.place-info');
                    if (infoDiv) infoDiv.innerHTML = `<p>${err.message}</p>`;
                });

            // Avis lieu
            fetch(`http://localhost:5001/api/v1/places/${placeId}/reviews/`, fetchOptions)
                .then(resp => resp.json())
                .then(reviews => {
                    const listDiv = document.getElementById('review-list');
                    if (!listDiv) return;
                    listDiv.innerHTML = '';
                    if (reviews.length === 0) {
                        listDiv.innerHTML = "<p>Aucun avis pour ce lieu.</p>";
                        return;
                    }
                    reviews.forEach(rv => {
                        const reviewCard = document.createElement('div');
                        reviewCard.className = 'review-card';
                        reviewCard.innerHTML = `
                            <p class="review-comment">${rv.text}</p>
                            <p class="review-user">Par ${rv.user_name || "Utilisateur inconnu"}</p>
                            <p class="review-rating">Note : ${rv.rating}/5</p>
                        `;
                        listDiv.appendChild(reviewCard);
                    });
                })
                .catch(err => {
                    const listDiv = document.getElementById('review-list');
                    if (listDiv) listDiv.innerHTML = `<p>Erreur chargement des avis : ${err.message}</p>`;
                });
        }
        fetchPlaceAndReviews();

        // Formulaire ajout avis
        const addReviewSection = document.getElementById('add-review');
        const reviewForm = document.getElementById('review-form');

        if (jwt) {
            if (addReviewSection) addReviewSection.style.display = 'block';

            if (reviewForm) {
                reviewForm.addEventListener('submit', (e) => {
                    e.preventDefault();

                    const text = document.getElementById('review-text').value.trim();
                    const rating = document.getElementById('review-rating').value;

                    if (!text || !rating) {
                        alert("Merci de remplir tous les champs.");
                        return;
                    }

                    fetch(`http://localhost:5001/api/v1/places/${placeId}/reviews/`, {
                        method: 'POST',
                        credentials: 'include',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': 'Bearer ' + jwt
                        },
                        body: JSON.stringify({ text, rating })
                    })
                        .then(resp => {
                            if (!resp.ok) throw new Error("Erreur lors de l'envoi de l'avis.");
                            return resp.json();
                        })
                        .then(() => {
                            reviewForm.reset();
                            fetchPlaceAndReviews();
                        })
                        .catch(err => {
                            alert(err.message || "Erreur inconnue");
                        });
                });
            }
        } else if (addReviewSection) {
            addReviewSection.innerHTML = `
                <a href="login.html" style="color: #007bff;">Connectez-vous pour laisser un avis</a>
            `;
        }
    }
});
