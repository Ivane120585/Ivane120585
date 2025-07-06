/**
 * Sacred Donation Widget
 * Stripe/BuyMe integration for ScrollBuilder donations
 */

class SacredDonationWidget {
    constructor(config = {}) {
        this.config = {
            builderId: config.builderId || 'scrollbuilder_2471',
            builderName: config.builderName || 'ScrollBuilder #2471',
            flameLevel: config.flameLevel || 4,
            sealLevel: config.sealLevel || 4,
            currency: config.currency || 'USD',
            flameRequired: config.flameRequired || 2,
            ...config
        };
        
        this.donationTiers = {
            flame_supporter: {
                name: 'Flame Supporter',
                amount: 5,
                description: 'Basic support for sacred development',
                benefits: ['Flame Supporter badge', 'Access to supporter scrolls', 'Monthly updates'],
                color: '#FF6F00',
                icon: '🔥'
            },
            keeper_sponsor: {
                name: 'Keeper Sponsor',
                amount: 15,
                description: 'Dedicated support for flame verification',
                benefits: ['Keeper Sponsor badge', 'Priority feature access', 'Quarterly reports'],
                color: '#FFD700',
                icon: '🛡️'
            },
            seer_founder: {
                name: 'Seer Founder',
                amount: 50,
                description: 'Elite support for prophetic governance',
                benefits: ['Seer Founder badge', 'Direct council access', 'Custom tools'],
                color: '#4A148C',
                icon: '🔮'
            },
            tithe_builder: {
                name: 'Tithe Builder',
                amount: 100,
                description: 'Ultimate support for sacred ecosystem',
                benefits: ['Tithe Builder badge', 'Founding member status', 'Lifetime access'],
                color: '#FF0000',
                icon: '👑'
            }
        };
        
        this.init();
    }
    
    init() {
        this.createWidget();
        this.bindEvents();
        this.loadStripe();
    }
    
    createWidget() {
        const widgetHTML = `
            <div id="sacred-donation-widget" class="sacred-donation-widget">
                <div class="widget-header">
                    <h3>🔥 Support Sacred Development</h3>
                    <p>Help ${this.config.builderName} continue creating flame-verified scroll products</p>
                </div>
                
                <div class="flame-status">
                    <span class="flame-indicator">🔥</span>
                    <span>Flame Level ${this.config.flameLevel} • Seal Level ${this.config.sealLevel}</span>
                </div>
                
                <div class="donation-tiers">
                    ${Object.entries(this.donationTiers).map(([key, tier]) => `
                        <div class="donation-tier" data-tier="${key}" data-amount="${tier.amount}">
                            <div class="tier-header">
                                <span class="tier-icon">${tier.icon}</span>
                                <span class="tier-name">${tier.name}</span>
                            </div>
                            <div class="tier-amount">$${tier.amount}</div>
                            <div class="tier-description">${tier.description}</div>
                            <div class="tier-benefits">
                                ${tier.benefits.map(benefit => `<div class="benefit-item">• ${benefit}</div>`).join('')}
                            </div>
                        </div>
                    `).join('')}
                </div>
                
                <div class="custom-donation">
                    <label for="custom-amount">Custom Amount ($)</label>
                    <input type="number" id="custom-amount" min="1" step="1" placeholder="Enter amount">
                </div>
                
                <div class="donation-summary" style="display: none;">
                    <h4>Donation Summary</h4>
                    <div class="summary-details">
                        <div class="summary-item">
                            <span>Amount:</span>
                            <span id="summary-amount">$0</span>
                        </div>
                        <div class="summary-item">
                            <span>Tier:</span>
                            <span id="summary-tier">None</span>
                        </div>
                        <div class="summary-item">
                            <span>Builder Receives:</span>
                            <span id="summary-builder-amount">$0</span>
                        </div>
                        <div class="summary-item">
                            <span>Ecosystem Fund:</span>
                            <span id="summary-ecosystem-amount">$0</span>
                        </div>
                    </div>
                </div>
                
                <div class="donation-actions">
                    <button id="donate-button" class="donate-button" disabled>
                        🔥 Make Sacred Donation
                    </button>
                    <div class="payment-methods">
                        <span>Payment Methods:</span>
                        <div class="payment-icons">
                            <span class="payment-icon">💳</span>
                            <span class="payment-icon">🪙</span>
                            <span class="payment-icon">📱</span>
                        </div>
                    </div>
                </div>
                
                <div class="donation-footer">
                    <p>Your donation supports sacred development and flame verification</p>
                    <p>70% goes directly to the ScrollBuilder • 30% supports ecosystem development</p>
                </div>
            </div>
        `;
        
        // Create widget container
        const container = document.createElement('div');
        container.innerHTML = widgetHTML;
        
        // Add styles
        this.addStyles();
        
        // Append to page
        document.body.appendChild(container);
    }
    
    addStyles() {
        const styles = `
            <style>
                .sacred-donation-widget {
                    background: linear-gradient(135deg, #1A1A1A 0%, #4A148C 100%);
                    border-radius: 20px;
                    padding: 2rem;
                    color: #FFFFFF;
                    font-family: 'ScrollCode', 'Courier New', monospace;
                    max-width: 500px;
                    margin: 2rem auto;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.3);
                    border: 1px solid rgba(255,255,255,0.2);
                }
                
                .widget-header {
                    text-align: center;
                    margin-bottom: 2rem;
                }
                
                .widget-header h3 {
                    font-size: 1.5rem;
                    color: #FFD700;
                    margin-bottom: 0.5rem;
                }
                
                .flame-status {
                    background: rgba(255,111,0,0.1);
                    border: 1px solid #FF6F00;
                    border-radius: 10px;
                    padding: 1rem;
                    text-align: center;
                    margin-bottom: 2rem;
                }
                
                .flame-indicator {
                    font-size: 1.2rem;
                    margin-right: 0.5rem;
                }
                
                .donation-tiers {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 1rem;
                    margin-bottom: 2rem;
                }
                
                .donation-tier {
                    background: rgba(255,255,255,0.1);
                    border-radius: 15px;
                    padding: 1.5rem;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    border: 2px solid transparent;
                }
                
                .donation-tier:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 10px 20px rgba(255,111,0,0.3);
                }
                
                .donation-tier.selected {
                    border-color: #FF6F00;
                    background: rgba(255,111,0,0.1);
                }
                
                .tier-header {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    margin-bottom: 1rem;
                }
                
                .tier-icon {
                    font-size: 1.5rem;
                }
                
                .tier-name {
                    font-weight: bold;
                    color: #FFD700;
                }
                
                .tier-amount {
                    font-size: 1.5rem;
                    font-weight: bold;
                    margin-bottom: 0.5rem;
                }
                
                .tier-description {
                    font-size: 0.9rem;
                    opacity: 0.8;
                    margin-bottom: 1rem;
                }
                
                .tier-benefits {
                    font-size: 0.8rem;
                }
                
                .benefit-item {
                    margin-bottom: 0.3rem;
                }
                
                .custom-donation {
                    margin-bottom: 2rem;
                }
                
                .custom-donation label {
                    display: block;
                    margin-bottom: 0.5rem;
                    color: #FFD700;
                }
                
                .custom-donation input {
                    width: 100%;
                    padding: 1rem;
                    background: rgba(255,255,255,0.1);
                    border: 1px solid rgba(255,255,255,0.3);
                    border-radius: 10px;
                    color: #FFFFFF;
                    font-size: 1rem;
                }
                
                .custom-donation input:focus {
                    outline: none;
                    border-color: #FF6F00;
                    box-shadow: 0 0 10px rgba(255,111,0,0.3);
                }
                
                .donation-summary {
                    background: rgba(255,255,255,0.05);
                    border-radius: 10px;
                    padding: 1.5rem;
                    margin-bottom: 2rem;
                }
                
                .donation-summary h4 {
                    color: #FFD700;
                    margin-bottom: 1rem;
                }
                
                .summary-item {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 0.5rem;
                }
                
                .donate-button {
                    width: 100%;
                    padding: 1rem 2rem;
                    background: linear-gradient(45deg, #FF6F00, #FFD700);
                    color: #1A1A1A;
                    border: none;
                    border-radius: 25px;
                    font-size: 1.1rem;
                    font-weight: bold;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }
                
                .donate-button:hover:not(:disabled) {
                    transform: scale(1.05);
                    box-shadow: 0 5px 15px rgba(255,111,0,0.4);
                }
                
                .donate-button:disabled {
                    opacity: 0.6;
                    cursor: not-allowed;
                }
                
                .payment-methods {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 1rem;
                    margin-top: 1rem;
                    font-size: 0.9rem;
                    opacity: 0.8;
                }
                
                .payment-icons {
                    display: flex;
                    gap: 0.5rem;
                }
                
                .payment-icon {
                    font-size: 1.2rem;
                }
                
                .donation-footer {
                    text-align: center;
                    margin-top: 2rem;
                    font-size: 0.9rem;
                    opacity: 0.8;
                }
                
                .donation-footer p {
                    margin-bottom: 0.5rem;
                }
                
                @media (max-width: 768px) {
                    .sacred-donation-widget {
                        margin: 1rem;
                        padding: 1.5rem;
                    }
                    
                    .donation-tiers {
                        grid-template-columns: 1fr;
                    }
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }
    
    bindEvents() {
        // Tier selection
        document.querySelectorAll('.donation-tier').forEach(tier => {
            tier.addEventListener('click', () => {
                this.selectTier(tier.dataset.tier);
            });
        });
        
        // Custom amount input
        document.getElementById('custom-amount').addEventListener('input', (e) => {
            this.handleCustomAmount(e.target.value);
        });
        
        // Donate button
        document.getElementById('donate-button').addEventListener('click', () => {
            this.processDonation();
        });
    }
    
    selectTier(tierKey) {
        // Remove previous selection
        document.querySelectorAll('.donation-tier').forEach(tier => {
            tier.classList.remove('selected');
        });
        
        // Select new tier
        const selectedTier = document.querySelector(`[data-tier="${tierKey}"]`);
        if (selectedTier) {
            selectedTier.classList.add('selected');
        }
        
        // Clear custom amount
        document.getElementById('custom-amount').value = '';
        
        // Update summary
        this.updateSummary(this.donationTiers[tierKey].amount, tierKey);
    }
    
    handleCustomAmount(value) {
        const amount = parseFloat(value) || 0;
        
        // Remove tier selection
        document.querySelectorAll('.donation-tier').forEach(tier => {
            tier.classList.remove('selected');
        });
        
        // Update summary
        this.updateSummary(amount, 'custom');
    }
    
    updateSummary(amount, tierKey) {
        const summaryElement = document.querySelector('.donation-summary');
        const donateButton = document.getElementById('donate-button');
        
        if (amount > 0) {
            // Calculate distribution
            const builderAmount = amount * 0.7; // 70% to builder
            const ecosystemAmount = amount * 0.3; // 30% to ecosystem
            
            // Update summary display
            document.getElementById('summary-amount').textContent = `$${amount.toFixed(2)}`;
            document.getElementById('summary-tier').textContent = tierKey === 'custom' ? 'Custom' : this.donationTiers[tierKey].name;
            document.getElementById('summary-builder-amount').textContent = `$${builderAmount.toFixed(2)}`;
            document.getElementById('summary-ecosystem-amount').textContent = `$${ecosystemAmount.toFixed(2)}`;
            
            // Show summary and enable button
            summaryElement.style.display = 'block';
            donateButton.disabled = false;
            
            // Store current donation data
            this.currentDonation = {
                amount: amount,
                tier: tierKey,
                builderAmount: builderAmount,
                ecosystemAmount: ecosystemAmount
            };
        } else {
            // Hide summary and disable button
            summaryElement.style.display = 'none';
            donateButton.disabled = true;
            this.currentDonation = null;
        }
    }
    
    async loadStripe() {
        // Load Stripe.js
        if (!window.Stripe) {
            const script = document.createElement('script');
            script.src = 'https://js.stripe.com/v3/';
            script.onload = () => this.initializeStripe();
            document.head.appendChild(script);
        } else {
            this.initializeStripe();
        }
    }
    
    initializeStripe() {
        // Initialize Stripe (replace with your publishable key)
        this.stripe = Stripe('pk_test_your_publishable_key_here');
    }
    
    async processDonation() {
        if (!this.currentDonation) {
            alert('Please select a donation amount');
            return;
        }
        
        // Check flame level requirement
        const userFlameLevel = localStorage.getItem('scrollSealLevel') || 1;
        if (userFlameLevel < this.config.flameRequired) {
            alert(`Flame Level ${this.config.flameRequired} required for donations. Current level: ${userFlameLevel}`);
            return;
        }
        
        try {
            // Show loading state
            const donateButton = document.getElementById('donate-button');
            const originalText = donateButton.textContent;
            donateButton.textContent = '🔥 Processing Sacred Donation...';
            donateButton.disabled = true;
            
            // Create payment intent
            const response = await fetch('/api/create-payment-intent', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    amount: this.currentDonation.amount * 100, // Convert to cents
                    currency: this.config.currency,
                    builder_id: this.config.builderId,
                    tier: this.currentDonation.tier,
                    flame_level: userFlameLevel
                })
            });
            
            const { clientSecret } = await response.json();
            
            // Confirm payment
            const result = await this.stripe.confirmCardPayment(clientSecret, {
                payment_method: {
                    card: this.elements.getElement('card'),
                    billing_details: {
                        name: 'Sacred Donation'
                    }
                }
            });
            
            if (result.error) {
                throw new Error(result.error.message);
            }
            
            // Success
            this.handleDonationSuccess(result.paymentIntent);
            
        } catch (error) {
            console.error('Donation error:', error);
            alert(`Sacred donation failed: ${error.message}`);
        } finally {
            // Reset button
            const donateButton = document.getElementById('donate-button');
            donateButton.textContent = '🔥 Make Sacred Donation';
            donateButton.disabled = false;
        }
    }
    
    handleDonationSuccess(paymentIntent) {
        // Log donation
        this.logDonation(paymentIntent);
        
        // Show success message
        alert(`🔥 Sacred donation successful! Thank you for supporting ${this.config.builderName}`);
        
        // Reset widget
        this.resetWidget();
        
        // Trigger success event
        this.triggerEvent('donation:success', {
            amount: this.currentDonation.amount,
            tier: this.currentDonation.tier,
            paymentIntent: paymentIntent
        });
    }
    
    logDonation(paymentIntent) {
        const donationLog = {
            timestamp: new Date().toISOString(),
            builder_id: this.config.builderId,
            amount: this.currentDonation.amount,
            tier: this.currentDonation.tier,
            payment_intent_id: paymentIntent.id,
            flame_level: localStorage.getItem('scrollSealLevel') || 1,
            builder_amount: this.currentDonation.builderAmount,
            ecosystem_amount: this.currentDonation.ecosystemAmount
        };
        
        // Send to server
        fetch('/api/log-donation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(donationLog)
        });
        
        // Store locally
        const donations = JSON.parse(localStorage.getItem('sacredDonations') || '[]');
        donations.push(donationLog);
        localStorage.setItem('sacredDonations', JSON.stringify(donations));
    }
    
    resetWidget() {
        // Clear selection
        document.querySelectorAll('.donation-tier').forEach(tier => {
            tier.classList.remove('selected');
        });
        
        // Clear custom amount
        document.getElementById('custom-amount').value = '';
        
        // Hide summary
        document.querySelector('.donation-summary').style.display = 'none';
        
        // Reset current donation
        this.currentDonation = null;
    }
    
    triggerEvent(eventName, data) {
        const event = new CustomEvent(eventName, {
            detail: data
        });
        document.dispatchEvent(event);
    }
    
    // Public methods
    getDonationHistory() {
        return JSON.parse(localStorage.getItem('sacredDonations') || '[]');
    }
    
    getTotalDonated() {
        const donations = this.getDonationHistory();
        return donations.reduce((total, donation) => total + donation.amount, 0);
    }
    
    updateBuilderInfo(builderId, builderName, flameLevel, sealLevel) {
        this.config.builderId = builderId;
        this.config.builderName = builderName;
        this.config.flameLevel = flameLevel;
        this.config.sealLevel = sealLevel;
        
        // Update display
        document.querySelector('.widget-header p').textContent = 
            `Help ${builderName} continue creating flame-verified scroll products`;
        document.querySelector('.flame-status span:last-child').textContent = 
            `Flame Level ${flameLevel} • Seal Level ${sealLevel}`;
    }
}

// Initialize widget
document.addEventListener('DOMContentLoaded', () => {
    window.sacredDonationWidget = new SacredDonationWidget({
        builderId: 'scrollbuilder_2471',
        builderName: 'ScrollBuilder #2471',
        flameLevel: 4,
        sealLevel: 4
    });
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SacredDonationWidget;
} 