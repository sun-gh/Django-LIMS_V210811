# Generated by Django 2.2 on 2022-01-11 13:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('demand_manage', '0006_auto_20220110_1708'),
    ]

    operations = [
        migrations.CreateModel(
            name='DemandDesign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.PositiveSmallIntegerField(choices=[(1, '待评估'), (2, '关闭'), (3, '待开发'), (4, '开发中'), (5, '已完成')], default=1, verbose_name='状态')),
                ('estimate_result', models.PositiveSmallIntegerField(choices=[(0, '无'), (1, '可实现'), (2, '不可行'), (3, '暂缓')], default=0, verbose_name='评估结果')),
                ('note', models.CharField(blank=True, max_length=300, null=True, verbose_name='评估建议')),
                ('predict_cycle', models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True, verbose_name='预计开发周期')),
                ('start_time', models.DateField(blank=True, null=True, verbose_name='开始时间')),
                ('finish_time', models.DateField(blank=True, null=True, verbose_name='完成时间')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('demand', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='demand_manage.DemandCollect', verbose_name='需求编号')),
            ],
            options={
                'verbose_name': '需求设计',
                'verbose_name_plural': '需求设计',
                'ordering': ['-create_time'],
            },
        ),
    ]