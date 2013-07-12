#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Eduardo Ochoa    <eduardo.ochoa@clusterbrands.com.ve>
#                               <elos3000@gmail.com>
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
{
    'name' : "Pos Fiscal Printer",
    'category' : "Test",
    'version' : "1.0",
    'depends' : ['pos_client'],
    'author' : "Me",
    'description' : """Pos Fiscal Printer""",
    'data' : [        
        'view/point_of_sale_view.xml',
    ],   
    'js':[   
        'static/src/js/models.js',
        'static/src/js/widgets.js',
        'static/src/js/devices.js',         
        'static/src/js/screens.js',       
        'static/src/js/main.js',                   
    ],
    'css': [
        'static/src/css/pos.css'
    ],
    'qweb': ['static/src/xml/pos.xml'],
}
