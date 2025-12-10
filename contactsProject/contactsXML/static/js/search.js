$(document).ready(function() {
    $('#search').on('keyup', function() {
        var query = $(this).val();
        searchContacts(query);
    });

    function searchContacts(query) {
        $.ajax({
            url: window.searchUrl,
            data: {'query': query},
            success: function(data) {
                var tbody = $('#contacts-table tbody');
                tbody.empty();
                if (data.length === 0) {
                    tbody.append('<tr><td colspan="5">Нет результатов.</td></tr>');
                } else {
                    data.forEach(function(c) {
                        tbody.append(`
                            <tr>
                                <td>${c.first_name}</td>
                                <td>${c.last_name}</td>
                                <td>${c.email}</td>
                                <td>${c.phone}</td>
                                <td>
                                    <a href="{% url 'contactsXML:edit_contact' c.id %}" class="btn btn-sm btn-warning">Редактировать</a>
                                    <a href="{% url 'contactsXML:delete_contact' c.id %}" class="btn btn-sm btn-danger">Удалить</a>
                                </td>
                            </tr>
                        `);
                    });
                }
            },
            error: function(xhr, status, error) {
                console.error("AJAX error: " + error);
                alert("Ошибка поиска: " + error);
            }
        });
    }
});