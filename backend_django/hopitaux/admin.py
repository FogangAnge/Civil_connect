from django.contrib import admin

from .models import DeclarationHopitaliere, Hopital


@admin.register(Hopital)
class HopitalAdmin(admin.ModelAdmin):
    list_display = ('code', 'nom', 'ville', 'user', 'created_at')
    search_fields = ('code', 'nom', 'user__email')


@admin.register(DeclarationHopitaliere)
class DeclarationHopitaliereAdmin(admin.ModelAdmin):
    list_display = ('id', 'hopital', 'mairie', 'type_declaration', 'nom', 'prenom', 'date_evenement', 'statut', 'created_at')
    list_filter = ('type_declaration', 'statut')
