$(document).ready(function() {
    $('#search').on('keyup', function() {
        var query = $(this).val();
        $.ajax({
            url: '{% url "contactsXML:search_contacts" %}',
            data: {'query': query},
            success: function(data) {
                var tbody = $('#contacts-table tbody');
                tbody.empty();
                data.forEach(function(c) {
                    tbody.append(`
                        <tr>
                            <td>${c.first_name}</td>
                            <td>${c.last_name}</td>
                            <td>${c.email}</td>
                            <td>${c.phone}</td>
                            <td>
                                <a href="/edit/${c.id}/" class="btn btn-sm btn-warning">Редактировать</a>
                                <a href="/delete/${c.id}/" class="btn btn-sm btn-danger">Удалить</a>
                            </td>
                        </tr>
                    `);
                });
            }
        });
    });
});