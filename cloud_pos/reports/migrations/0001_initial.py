# Generated by Django 5.1.2 on 2025-06-04 14:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SalesReport",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("report_date", models.DateField(auto_now_add=True)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("total_sales", models.DecimalField(decimal_places=2, max_digits=12)),
                ("total_orders", models.IntegerField()),
                ("total_items_sold", models.IntegerField()),
                (
                    "average_order_value",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("exported", models.BooleanField(default=False)),
                ("export_format", models.CharField(blank=True, max_length=10)),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["report_date"], name="reports_sal_report__92f498_idx"
                    ),
                    models.Index(
                        fields=["start_date", "end_date"],
                        name="reports_sal_start_d_de74dd_idx",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="InventoryAgingReport",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date_received", models.DateField()),
                ("quantity", models.IntegerField()),
                ("days_in_stock", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aging_reports",
                        to="products.product",
                    ),
                ),
            ],
            options={
                "ordering": ["-date_received"],
                "indexes": [
                    models.Index(
                        fields=["days_in_stock"], name="reports_inv_days_in_3db74e_idx"
                    ),
                    models.Index(
                        fields=["product", "date_received"],
                        name="reports_inv_product_1a5e57_idx",
                    ),
                ],
            },
        ),
    ]
