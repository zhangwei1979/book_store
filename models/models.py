# -*- coding: utf-8 -*-

from odoo import models, fields, api

class book_store(models.Model):
    _name = 'book_store.book'
    _description = 'book_store.book'
    _order = 'date_release desc, name'
    _rec_name = 'short_name'

    name = fields.Char()
    author = fields.Char()
    price = fields.Monetary(
        'Retail Price',
        # optional: currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        'res.currency', string='Currency')
    description = fields.Html()
    notes = fields.Text('Internal Notes')
    state = fields.Selection([
        ('draft', 'Unavailable'),
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('lost', 'Lost')],
        'State', default="draft")
    short_name = fields.Char('Short Title',translate=True, index=True)
    author_ids = fields.Many2many('res.partner', string='Authors')
    cover = fields.Binary('Book Cover')
    out_of_print = fields.Boolean('Out of Print?')
    date_release = fields.Date('Release Date')
    date_updated = fields.Datetime('Last Updated')
    pages = fields.Integer('Number of Pages',
                           groups='base.group_user',
                           states={'lost': [('readonly', True)]},
                           help='Total book page count', company_dependent=False)
    reader_rating = fields.Float('Reader Average Rating', digits=(14, 4),)

    publisher_id = fields.Many2one(
        'res.partner', string='Publisher',
        # optional:
        ondelete='set null',
        context={},
        domain=[],
    )

    @api.depends('value')
    def _value_pc(self):
        for record in self:
            record.value2 = float(record.value) / 100

    @api.model
    def is_allowed_transition(self, old_state, new_state):
        allowed = [('draft', 'available'),
                   ('available', 'borrowed'),
                   ('borrowed', 'available'),
                   ('available', 'lost'),
                   ('borrowed', 'lost'),
                   ('lost', 'available')]
        return (old_state, new_state) in allowed

    def change_state(self, new_state):
        for book in self:
            if book.is_allowed_transition(book.state, new_state):
                book.state = new_state
            else:
                continue

    def make_available(self):
        self.change_state('available')

    def make_borrowed(self):
        self.change_state('borrowed')

    def make_lost(self):
        self.change_state('lost')

class ResPartner(models.Model):
    _inherit = 'res.partner'

    published_book_ids = fields.One2many(
        'book_store.book', 'publisher_id',
        string='Published Books')

    authored_book_ids = fields.Many2many(
        'book_store.book',
        string='Authored Books',
        # relation='library_book_res_partner_rel' # optional
    )
