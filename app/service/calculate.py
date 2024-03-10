from datetime import datetime

from sqlalchemy import select

from app.crud.charity_project import charityproject_crud
from app.crud.donation import donation_crud
from app.models import CharityProject, Donation


async def calculate_create_project(
    obj_in,
    db_session
) -> dict:
    real_time = datetime.now()
    project_update_data = {
        'create_date': real_time
    }
    donat_update_data = {}
    donat_money = 0
    # Если в кубышке что-то есть, то заполняем проект
    async with db_session as session:
        get_not_ended_donations = await session.execute(select(
            Donation).where(Donation.fully_invested.is_(False))
        )
    not_ended_donations_list = get_not_ended_donations.scalars().all()

    for donation in not_ended_donations_list:
        # Не потраченные деньги из доната
        unallocated_money = donation.full_amount - donation.invested_amount
        # Считаем сколько нужно до закрытия проекта
        to_end_project = obj_in.full_amount - donat_money
        # Если сумма доната меньше нужной до закрытия проекта
        if unallocated_money < to_end_project:
            donat_update_data['invested_amount'] = donation.full_amount
            donat_update_data['fully_invested'] = True
            donat_update_data['close_date'] = real_time
            await donation_crud.update(donation, donat_update_data, db_session)
            donat_money += unallocated_money
            continue
        # Если сумма доната больше нужной до закрытия проекта
        if unallocated_money > to_end_project:
            donat_update_data['invested_amount'] = (donation.invested_amount +
                                                    to_end_project)
        # Если сумма доната равна нужной до закрытия проекта
        else:
            donat_update_data['invested_amount'] = donation.full_amount
            donat_update_data['fully_invested'] = True
            donat_update_data['close_date'] = real_time
        await donation_crud.update(donation, donat_update_data, db_session)
        project_update_data['invested_amount'] = obj_in.full_amount
        project_update_data['close_date'] = real_time
        project_update_data['fully_invested'] = True
        break

    return project_update_data


async def calculate_create_donation(
    obj_in,
    db_session
) -> dict:
    real_time = datetime.now()
    obj_in_data = {
        'create_date': real_time,
    }
    donation_sum = obj_in.full_amount
    invested_amount = 0
    # Берём не завершённые проекты
    async with db_session as session:
        active_projects = await session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested.is_(False))
        )
    active_projects_list = active_projects.scalars().all()

    for get_active_project in active_projects_list:
        # - Проверяем, есть ли куда донатить и есть ли на статье не
        # потраченные деньги.
        # - Если активных проектов нет, а деньги
        # остались, то не закрываем донат и отмечаем сумму израсзрдованных
        # денег из доната.
        # - Если все деньги потрачены, то донат обозначаем как выплаченный.
        # - Если есть не завершённый проект и деньги не потрачены,
        # то производим расчёт сколько нужно до закрытия проекта.
        if donation_sum == 0:
            obj_in_data['invested_amount'] = obj_in.full_amount
            obj_in_data['fully_invested'] = True
            obj_in_data['close_date'] = real_time
            break

        sum_to_end_project = (get_active_project.full_amount -
                              get_active_project.invested_amount)
        # - Если сумма до завершения проекта меньше или ровна сумме доната,
        # то делаем выплату в проект, проект обозначаем как
        # завершённый, а деньги пускаем в новый оборот
        # к следующему проекту.
        # - Если сумма до закрытия проекта меньше доната, то делаем
        # выплату и обозначаем донат закрытым.
        if sum_to_end_project < donation_sum:
            donation_sum -= sum_to_end_project
            invested_amount += sum_to_end_project
            obj_in_data['invested_amount'] = invested_amount
            new_update_data = {
                'fully_invested': True,
                'invested_amount': get_active_project.full_amount,
                'close_date': real_time
            }
            await charityproject_crud.update(
                db_obj=get_active_project,
                obj_in=new_update_data,
                db_session=db_session
            )
            continue

        obj_in_data['invested_amount'] = obj_in.full_amount
        obj_in_data['fully_invested'] = True
        obj_in_data['close_date'] = real_time
        new_update_data = {
            'invested_amount': (get_active_project.invested_amount +
                                donation_sum)
        }
        if (get_active_project.invested_amount + donation_sum
                == get_active_project.full_amount):
            new_update_data['fully_invested'] = True

        await charityproject_crud.update(
            db_obj=get_active_project,
            obj_in=new_update_data,
            db_session=db_session
        )
        break

    return obj_in_data
