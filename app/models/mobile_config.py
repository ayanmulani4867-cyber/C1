from datetime import datetime
from app.extensions import db


class MobileAppConfig(db.Model):
    __tablename__ = 'mobile_app_configs'

    id = db.Column(db.Integer, primary_key=True)
    config_version = db.Column(db.String(20), default='1.0', nullable=False)
    maintenance_mode = db.Column(db.Boolean, default=False, nullable=False)
    maintenance_message = db.Column(db.String(255), default='System maintenance in progress. Please check back shortly.', nullable=False)
    min_app_version = db.Column(db.String(20), default='1.0.0', nullable=False)
    update_url = db.Column(db.String(255), default='', nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'config_version': self.config_version,
            'maintenance_mode': self.maintenance_mode,
            'maintenance_message': self.maintenance_message,
            'min_app_version': self.min_app_version,
            'update_url': self.update_url,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class MobileHomeSection(db.Model):
    __tablename__ = 'mobile_home_sections'

    id = db.Column(db.Integer, primary_key=True)
    section_key = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    is_enabled = db.Column(db.Boolean, default=True, nullable=False)
    display_order = db.Column(db.Integer, default=1, nullable=False)

    def to_dict(self):
        return {
            'id': self.section_key,
            'name': self.name,
            'enabled': self.is_enabled,
            'order': self.display_order
        }


class MobileQuickAction(db.Model):
    __tablename__ = 'mobile_quick_actions'

    id = db.Column(db.Integer, primary_key=True)
    action_key = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    route = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(50), default='default', nullable=False)
    is_enabled = db.Column(db.Boolean, default=True, nullable=False)
    display_order = db.Column(db.Integer, default=1, nullable=False)

    def to_dict(self):
        return {
            'id': self.action_key,
            'title': self.title,
            'route': self.route,
            'icon': self.icon,
            'enabled': self.is_enabled,
            'order': self.display_order
        }


class MobileBanner(db.Model):
    __tablename__ = 'mobile_banners'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    subtitle = db.Column(db.String(255), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    action_url = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    display_order = db.Column(db.Integer, default=1, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'subtitle': self.subtitle,
            'image_url': self.image_url,
            'action_url': self.action_url,
            'is_active': self.is_active,
            'order': self.display_order
        }


class MobileFeatureFlag(db.Model):
    __tablename__ = 'mobile_feature_flags'

    id = db.Column(db.Integer, primary_key=True)
    flag_key = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    is_enabled = db.Column(db.Boolean, default=True, nullable=False)

    def to_dict(self):
        return {
            'key': self.flag_key,
            'name': self.name,
            'enabled': self.is_enabled
        }
