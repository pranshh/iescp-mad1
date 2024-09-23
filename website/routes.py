from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from .models import User, Sponsor, Influencer, Campaign, AdRequest
from . import db
from flask import request, jsonify, abort
from datetime import datetime


main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_flagged:
        return render_template('flagged.html')
    if current_user.role == 'admin':
        return redirect(url_for('main.admin_dashboard'))
    elif current_user.role == 'sponsor':
        return redirect(url_for('main.sponsor_dashboard'))
    elif current_user.role == 'influencer':
        return redirect(url_for('main.influencer_dashboard'))

@main.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    users = User.query.all()
    sponsors = Sponsor.query.all()
    influencers = Influencer.query.all()
    campaigns = Campaign.query.all()
    ad_requests = AdRequest.query.all()
    
    return render_template('admin_dashboard.html', 
                           users=users, 
                           sponsors=sponsors, 
                           influencers=influencers, 
                           campaigns=campaigns, 
                           ad_requests=ad_requests)

@main.route('/sponsor_dashboard')
@login_required
def sponsor_dashboard():
    if current_user.role != 'sponsor':
        flash('Access denied. Sponsor privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    sponsor = Sponsor.query.get(current_user.id)
    campaigns = Campaign.query.filter_by(sponsor_id=current_user.id).all()
    pending_requests = AdRequest.query.join(Campaign).filter(Campaign.sponsor_id == current_user.id, AdRequest.status == 'pending').all()
    approved_requests = AdRequest.query.join(Campaign).filter(Campaign.sponsor_id == current_user.id, AdRequest.status == 'approved').all()
    
    return render_template('sponsor_dashboard.html', 
                           sponsor=sponsor,
                           campaigns=campaigns,
                           pending_requests=pending_requests,
                           approved_requests=approved_requests)

@main.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if current_user.role == 'sponsor':
        profile = Sponsor.query.get(current_user.id)
    elif current_user.role == 'influencer':
        profile = Influencer.query.get(current_user.id)
    else:
        flash('Invalid user role.', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        current_user.name = request.form.get('name')
        current_user.email = request.form.get('email')

        if current_user.role == 'sponsor':
            profile.company_name = request.form.get('company_name')
            profile.industry = request.form.get('industry')
            profile.budget = float(request.form.get('budget'))
        elif current_user.role == 'influencer':
            profile.category = request.form.get('category')
            profile.niche = request.form.get('niche')
            profile.reach = int(request.form.get('reach'))

        db.session.commit()
        flash('Your profile has been updated successfully.', 'success')
        return redirect(url_for(f'main.{current_user.role}_dashboard'))

    return render_template('edit_profile.html', user=current_user, profile=profile)

@main.route('/create_campaign', methods=['GET', 'POST'])
@login_required
def create_campaign():
    if current_user.role != 'sponsor':
        flash('Access denied. Sponsor privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
        budget = float(request.form.get('budget'))
        goals = request.form.get('goals')
        
        new_campaign = Campaign(
            sponsor_id=current_user.id,
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            status='active', 
            goals=goals
        )
        db.session.add(new_campaign)
        db.session.commit()
        flash('Campaign created successfully!', 'success')
        return redirect(url_for('main.sponsor_dashboard'))
    return render_template('create_campaign.html')

@main.route('/update_campaign/<int:campaign_id>', methods=['GET', 'POST'])
@login_required
def update_campaign(campaign_id):
    if current_user.role != 'sponsor':
        flash('Access denied. Sponsor privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.sponsor_id != current_user.id:
        flash('Access denied. You can only update your own campaigns.', 'error')
        return redirect(url_for('main.sponsor_dashboard'))
    
    if request.method == 'POST':
        campaign.title = request.form.get('title')
        campaign.description = request.form.get('description')
        campaign.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
        campaign.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
        campaign.budget = float(request.form.get('budget'))
        campaign.goals = request.form.get('goals')
        db.session.commit()
        flash('Campaign updated successfully!', 'success')
        return redirect(url_for('main.sponsor_dashboard'))
    
    return render_template('update_campaign.html', campaign=campaign)

@main.route('/delete_campaign/<int:campaign_id>', methods=['POST'])
@login_required
def delete_campaign(campaign_id):
    if current_user.role != 'sponsor':
        flash('Access denied. Sponsor privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.sponsor_id != current_user.id:
        flash('Access denied. You can only delete your own campaigns.', 'error')
        return redirect(url_for('main.sponsor_dashboard'))
        
    db.session.delete(campaign)
    db.session.commit()
    flash('Campaign deleted successfully!', 'success')
    return redirect(url_for('main.sponsor_dashboard'))

@main.route('/create_ad_request/<int:campaign_id>', methods=['GET', 'POST'])
@login_required
def create_ad_request(campaign_id):
    
    if current_user.role != 'sponsor':
        flash('Access denied. Sponsor privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.sponsor_id != current_user.id:
        flash('Access denied. You can only create ad requests for your own campaigns.', 'error')
        return redirect(url_for('main.sponsor_dashboard'))
    
    if request.method == 'POST':
        influencer_id = request.form.get('influencer_id')
        message = request.form.get('message')
        requirements = request.form.get('requirements')
        payment_amount = float(request.form.get('payment_amount'))
        
        new_ad_request = AdRequest(
            campaign_id=campaign_id,
            influencer_id=influencer_id,
            message=message,
            requirements=requirements,
            payment_amount=payment_amount,
            status='pending'
        )
        db.session.add(new_ad_request)
        db.session.commit()
        flash('Ad request created successfully!', 'success')
        return redirect(url_for('main.sponsor_dashboard'))
    
    influencers = Influencer.query.all()
    return render_template('create_ad_request.html', campaign=campaign, influencers=influencers)

@main.route('/edit_ad_request/<int:request_id>', methods=['GET', 'POST'])
@login_required
def edit_ad_request(request_id):
    if current_user.role != 'sponsor':
        flash('Access denied. Sponsor privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    ad_request = AdRequest.query.get_or_404(request_id)
    if ad_request.campaign.sponsor_id != current_user.id:
        flash('Access denied. You can only edit ad requests for your own campaigns.', 'error')
        return redirect(url_for('main.sponsor_dashboard'))
    
    if request.method == 'POST':
        ad_request.message = request.form.get('message')
        ad_request.requirements = request.form.get('requirements')
        ad_request.payment_amount = float(request.form.get('payment_amount'))
        db.session.commit()
        flash('Ad request updated successfully!', 'success')
        return redirect(url_for('main.sponsor_dashboard'))
    
    return render_template('edit_ad_request.html', ad_request=ad_request)

@main.route('/approve_request/<int:request_id>')
@login_required
def approve_request(request_id):
    if current_user.role != 'sponsor':
        return jsonify({'error': 'Access denied'}), 403
    
    ad_request = AdRequest.query.get_or_404(request_id)
    if ad_request.campaign.sponsor_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    ad_request.status = 'approved'
    db.session.commit()
    return jsonify({'message': 'Request approved successfully'}), 200

@main.route('/reject_request/<int:request_id>')
@login_required
def reject_request(request_id):
    if current_user.role != 'sponsor':
        return jsonify({'error': 'Access denied'}), 403
    
    ad_request = AdRequest.query.get_or_404(request_id)
    if ad_request.campaign.sponsor_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    ad_request.status = 'rejected'
    db.session.commit()
    return jsonify({'message': 'Request rejected successfully'}), 200

@main.route('/influencer_approve_request/<int:request_id>')
@login_required
def sponsor_approve_request(request_id):
    if current_user.role != 'influencer':
        flash('Access denied. influencer privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    ad_request = AdRequest.query.get_or_404(request_id)
    
    if current_user.role != 'influencer':
        flash('Access denied. You can only respond to requests for your own campaigns.', 'error')
        return redirect(url_for('main.influencer_dashboard'))
    
    ad_request.status = 'approved'
    db.session.commit()
    flash('Ad request approved successfully.', 'success')
    return redirect(url_for('main.influencer_dashboard'))

@main.route('/influencer_reject_request/<int:request_id>')
@login_required
def sponsor_reject_request(request_id):
    if current_user.role != 'influencer':
        flash('Access denied. Influencer privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    ad_request = AdRequest.query.get_or_404(request_id)
    
    if current_user.role != 'influencer':
        flash('Access denied. You can only respond to requests for your own campaigns.', 'error')
        return redirect(url_for('main.influencer_dashboard'))
    
    db.session.delete(ad_request)
    db.session.commit()
    flash('Ad request rejected successfully.', 'success')
    return redirect(url_for('main.influencer_dashboard'))

@main.route('/search_influencers', methods=['GET', 'POST'])
@login_required
def search_influencers():
    if current_user.role != 'sponsor':
        flash('Access denied. Sponsor privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    query = request.form.get('query')
    influencers = Influencer.query.filter(Influencer.niche.like(f'%{query}%')).all()
    return render_template('search_influencers.html', influencers=influencers)

@main.route('/influencer_dashboard')
@login_required
def influencer_dashboard():
    if current_user.role != 'influencer':
        flash('Access denied. Influencer privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    ad_requests = AdRequest.query.filter_by(influencer_id=current_user.id).all()
    
    influencer = Influencer.query.get(current_user.id)
    pending_requests = AdRequest.query.filter_by(influencer_id=current_user.id, status='pending').all()
    active_campaigns = AdRequest.query.filter_by(influencer_id=current_user.id, status='approved').all()
    available_campaigns = Campaign.query.filter_by(status='active').all()
    
    # Remove campaigns that the influencer has already applied to or are active
    applied_campaign_ids = [req.campaign_id for req in pending_requests + active_campaigns]
    available_campaigns = [camp for camp in available_campaigns if camp.id not in applied_campaign_ids]
    
    return render_template('influencer_dashboard.html', 
                           influencer=influencer,
                           pending_requests=pending_requests,
                           active_campaigns=active_campaigns,
                           available_campaigns=available_campaigns)

@main.route('/apply_to_campaign/<int:campaign_id>', methods=['GET', 'POST'])
@login_required
def apply_to_campaign(campaign_id):
    if current_user.role != 'influencer':
        flash('Access denied. Influencer privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if request.method == 'POST':
        message = request.form.get('message')
        proposed_budget = float(request.form.get('proposed_budget'))
        
        new_request = AdRequest(
            campaign_id=campaign_id,
            influencer_id=current_user.id,
            message=message,
            requirements=None,
            payment_amount=proposed_budget,
            status='pending'
        )
        db.session.add(new_request)
        db.session.commit()
        flash('Your application has been submitted successfully.', 'success')
        return redirect(url_for('main.influencer_dashboard'))
    return render_template('apply_to_campaign.html', campaign=campaign)

@main.route('/respond_to_request/<int:request_id>/<action>')
@login_required
def respond_to_request(request_id, action):
    if current_user.role != 'influencer':
        return jsonify({'error': 'Access denied. Influencer privileges required.'}), 403
    
    ad_request = AdRequest.query.get_or_404(request_id)
    
    if ad_request.influencer_id != current_user.id:
        return jsonify({'error': 'Access denied. You can only respond to your own requests.'}), 403
    
    if action not in ['approve', 'reject']:
        return jsonify({'error': 'Invalid action.'}), 400
    
    ad_request.respond(action)
    return jsonify({
        'message': f'Ad request {action}d successfully.',
        'new_status': ad_request.status,
        'campaign_id': ad_request.campaign_id,
        'campaign_title': ad_request.campaign.title,
        'sponsor_name': ad_request.campaign.sponsor.user.name,
        'start_date': ad_request.campaign.start_date.strftime('%Y-%m-%d'),
        'end_date': ad_request.campaign.end_date.strftime('%Y-%m-%d'),
        'budget': ad_request.campaign.budget,
    }), 200

@main.route('/flag/<string:model>/<int:id>')
@login_required
def flag_item(model, id):
    if current_user.role != 'admin':
        abort(403) 

    if model == 'user':
        item = User.query.get_or_404(id)
    elif model == 'campaign':
        item = Campaign.query.get_or_404(id)
    else:
        abort(404) 

    item.is_flagged = not item.is_flagged
    db.session.commit()
    flash(f'{model.capitalize()} {"flagged" if item.is_flagged else "unflagged"} successfully', 'success')
    return redirect(url_for('main.admin_dashboard'))