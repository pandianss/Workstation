import React, { useState } from 'react';
import CircularList from './CircularList';
import CircularForm from './CircularForm';

const CircularManager = () => {
    // Mode: 'list' | 'create' | 'edit'
    const [mode, setMode] = useState('list');
    const [selectedCircular, setSelectedCircular] = useState(null);

    return (
        <div style={{ position: 'relative' }}>
            {mode === 'list' && (
                <CircularList
                    onCreateNew={() => {
                        setSelectedCircular(null);
                        setMode('create');
                    }}
                    onSelect={(circular) => {
                        setSelectedCircular(circular);
                        setMode('edit');
                    }}
                />
            )}

            {(mode === 'create' || mode === 'edit') && (
                <CircularForm
                    onBack={() => {
                        setMode('list');
                        setSelectedCircular(null);
                    }}
                    initialData={selectedCircular}
                />
            )}
        </div>
    );
};

export default CircularManager;
