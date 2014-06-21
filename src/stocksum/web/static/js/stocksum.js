$(function(){
    $('#form-new-portfolio').submit(function(event){
        event.preventDefault();
        var name = prompt('Enter the name of the new portfolio:', '');
        if ((name === null) || (name == ''))
            return;
        $('#inp-new-portfolio-name').val(name);
        $.post('/portfolios/new', $(this).serialize(), function(data){
            location.href = '/portfolios?id='+data['id'].toString();
        }, 'json');
    });

    $('#form-portfolio-add-transaction').submit(function(event){
        event.preventDefault();
        $('#portfolio-transactions tbody').append(_.template(multiline(function(){/*
            <tr>
                <td><input type="hidden" name="index" value="-1"><input class="form-control" type="text" name="symbol" value="<%- symbol %>"></td>
                <td><input class="form-control" type="text" name="trade_date" value="<%- trade_date %>"></td>
                <td><input class="form-control" type="text" name="shares" value="<%- shares %>"></td>
                <td><input class="form-control" type="text" name="paid_price" value="<%- paid_price %>"></td>
                <td></td>
            </tr>
        */}), {
            symbol: $(this).find('input[name=symbol]').val(),
            trade_date: $(this).find('input[name=trade_date]').val(),
            shares: $(this).find('input[name=shares]').val(),
            paid_price: $(this).find('input[name=paid_price]').val(),
        }));
        $(this).find('input[name=symbol]').val('');
        $(this).find('input[name=trade_date]').val('');
        $(this).find('input[name=shares]').val('');
        $(this).find('input[name=paid_price]').val('');
        $(this).find('input[name=symbol]').focus();
        $('#form-portfolio-transactions').find('.no-transactions').remove();
    });
    $('#form-portfolio-transactions').submit(function(event){
        event.preventDefault();
        var id = $(this).find('input[name=id]').val();
        $.post('/portfolio-edit-transactions?id='+id, $(this).serialize(), function(data){
            location.href = '/portfolio-edit-transactions?id='+id;
        });
    });

    $('#form-portfolio-add-cron').submit(function(){
        event.preventDefault();
        var id = $(this).find('input[name=id]').val();
        $.post('/portfolio-new-cron?id='+id, $(this).serialize(), function(data){
            location.href = '/portfolio-edit-crontab?id='+id;
        });
    });
    $('#form-portfolio-crontab').submit(function(event){
        event.preventDefault();
        var id = $(this).find('input[name=id]').val();
        $.post('/portfolio-edit-crontab?id='+id, $(this).serialize(), function(data){
            location.href = '/portfolio-edit-crontab?id='+id;
        });
    });

    $('#form-settings').submit(function(event){
        event.preventDefault();
        $.post('/settings', $(this).serialize(), function(data){
            location.href = '/settings';
        });
    });
});