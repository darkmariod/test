<?php

namespace App\Filament\Resources\ResumenDiarioResource\Pages;

use App\Filament\Resources\ResumenDiarioResource;
use Filament\Actions;
use Filament\Resources\Pages\ListRecords;

class ListResumenDiarios extends ListRecords
{
    protected static string $resource = ResumenDiarioResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\CreateAction::make(),
        ];
    }
}
